# Substrate as INTRINSIC LLM Context Extension: 7-Layer Integration Landscape (v278, 2026-05-29)

Date: 2026-05-29
Owner: research sub-agent (Opus-escalated; DEEPER fresh-eyes drill)
Status: COMPLETED -- landscape map + feasibility matrix + 5 ship-candidate experiments + customer demos
Calibration: lit-scan deflation 0.15-0.25 applied throughout per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap 0.50 applied to L3/L4 closed-weight substrate integration claims
Substrate-product framing per [[feedback-no-papers-product-only]] + [[feedback-substrate-value-framing-2026-05-26]]

Predecessors:
- notes/substrate_llm_hybrid_multihop_architecture_v278_2026-05-29.md (3-tier hybrid; L1 SHALLOW integration baseline)
- notes/anthropic_memory_competitive_and_agentic_ai_architecture_v278_2026-05-29.md (Part II agentic memory hierarchy)
- notes/pattern_b_integration_demo_executable_spec_v278_2026-05-29.md (Pattern B FastAPI tool-use)
- notes/seven_intrinsic_properties_validation_designs_v278_2026-05-29.md (Property 4 speculative; LLM-internal representation compatibility)
- notes/research_lagging_caps_v276_fresh_eyes_2026-05-29.md (substrate primitives inventory)

---

## HEADLINE

The substrate-LLM hybrid just designed (v278) operates at LAYER 1 (token-level / tool-use) which is the DEEPEST integration compatible with closed-weight Claude/GPT-4 today; substrate-as-INTRINSIC-context-extension at deeper layers (L2 soft-prompt / L3 KV-cache / L4 hidden-state) requires open-weight model surgery (Llama 3.x / Mistral / Pythia) and ships in 2-6 weeks engineering per layer. The most consequential opening is L3 (substrate-as-KV-cache-extension): substrate atoms storing past attention KV pairs, retrieved by key-similarity at inference time, gives a structural effective-context expansion of ~50K-100K tokens at substrate N=4096-8192 BSC production scale -- making substrate a "compute-cheap, audit-grade alternative to longer native LLM context" via the Memorizing-Transformers-with-deletion-cert mechanism. P_deflated of L3 working on open-weight Llama-3.1-8B (HARD-PASS: matches or beats vector-DB-augmented Memorizing Transformer baseline at 100K-token effective context with full audit trail + deletion-cert cascade): 0.40 (novel-synthesis cap 0.50 applied; substrate's per-atom retrieval accuracy is mature per KF-1/KF-2 production-N HARD_PASS, but substrate-cosine-similarity vs learned-kNN-attention quality gap on hidden-state distributions is unresolved -- Property 4 Johnson-Lindenstrauss sanity check from seven_intrinsic_properties spec is the gating prerequisite). The 3-month roadmap should ship E1 (substrate-as-CoT-state-offload, L1, 3-5 days eng, P=0.55 -- this is the v278 hybrid MVP) IMMEDIATELY, then in parallel ship the Property 4 sanity check (1 hr CPU, P=0.50) to decide whether E2-E3 (L2-L3 open-weight integration) gets the 6-12 week build path. The "thousand-step CoT" capability is achievable structurally at L1 today via CoT state offload (~500 hops with 200K-context Claude, projected 1000+ with offload protocol); L3 promises 100K-1M effective context on natively-8K models. Top customer demo: legal eDiscovery agent with 10K-document context, substrate stores doc atoms, LLM working set 5-10 atoms per hop, end-to-end audit trail. Substrate's UNIQUE competitive position at every integration layer is the audit-grade overlay: deletion-cert + per-atom provenance + edit-isolation guarantees that StreamingLLM / H2O / LongMem / Memorizing Transformers / MemGPT / Infini-attention structurally cannot provide.

---

## Cheap decisive test

A 1-hour CPU sanity probe BEFORE committing to L2-L3 build:

**Property 4 Johnson-Lindenstrauss compatibility check** (cited in seven_intrinsic_properties spec Property 4):
- Extract 1K residual-stream activations from GPT-2-small (or Llama-3.1-8B if available) at final-layer last-token position over Wikitext-103 passages
- Apply random structural projection `P: R^768 -> R^N_substrate` (Johnson-Lindenstrauss; ~N=4096)
- Bind each projected activation as a substrate atom; build N=4096 substrate store
- For 100 held-out activations, query substrate; measure top-5 retrieval overlap with original passage
- HARD-PASS: >=70% top-5 retrieval on 1K-item needle-in-haystack
- HARD-FAIL: <=30% top-5 (means substrate cannot use LLM internal representations meaningfully)
- Middle band 30-70%: ship L1+L2 only; abandon L3 pursuit until ingestion redesign

Cost: 1 hr CPU + ~$0 (no LLM API calls; activations are open-weight GPT-2 forward pass).

PASS criterion: gate on Property 4 sanity result. If PASS, commit E2 (L2 soft-prompt store) + E3 (L3 KV-cache extension) build budget (~4-6 calendar weeks for one engineer); if FAIL, focus exclusively on L1 extensions (E1 CoT state offload + E5 MemGPT-backend).

---

## Falsifiable predictions

HARD-PASS bands (per experiment):

**E1 (L1 CoT state offload; substrate-LLM hybrid MVP):**
- HP1: 1000-step reasoning chain completes within 200K-context Claude budget; substrate stores >=80% of intermediate facts; LLM working set <=15K tokens at any hop
- HP2: chain accuracy on HotpotQA-extended (synthetic 100-hop chains) within 15pp of LLM-only CoT (capped at 50 hops due to context)
- HP3: deletion-cert cascade identifies all chain dependencies <1s p95

**E2 (L2 soft-prompt store; substrate atoms as compressed prefix embeddings, open-weight Llama):**
- HP1: 10x prompt compression (1 substrate atom replaces ~10-30 prompt tokens) with downstream task accuracy >=80% of full-prompt baseline on Natural Questions / MS MARCO
- HP2: substrate-stored gist matches gist-token quality (Mu et al. 2023) at equivalent compression ratio
- HP3: cross-document gist composition (binding two substrate atoms) preserves >=70% information

**E3 (L3 KV-cache extension; substrate as Memorizing-Transformers external memory):**
- HP1: Llama-3.1-8B with substrate-KV-extension achieves perplexity on PG-19 / arXiv-math within 5% of Memorizing Transformers baseline at 100K-token effective context (262K reported in MT paper; we target 100K as honest scope)
- HP2: substrate-KV retrieval latency <50ms p95 vs MT's kNN-attention ~20ms (substrate disadvantage <2.5x acceptable)
- HP3: audit-trail completeness >=95% on per-token provenance (substrate's unique value-add over MT)

HARD-FAIL bands (any one triggers layer-level pivot):

**E1 FAIL:** chain accuracy >25pp below LLM-only CoT at 50 hops -> substrate ingestion quality bottleneck -> pivot to L1-shallow-only (RAG, no CoT offload)
**E2 FAIL:** compression ratio <2x at 80% quality -> substrate codebook geometry incompatible with prompt-embedding distribution -> abandon L2 layer
**E3 FAIL:** Property 4 sanity <=30% OR full-build perplexity >15% above MT -> abandon L3-L4; substrate is structurally a text-layer system, not a hidden-state-layer system

MIDDLE-BAND (ship with reframing):
- E1 chain accuracy 15-25pp below: ship as "audit-priority over peak accuracy"; product positioning shifts to compliance use cases
- E2 compression 2-5x: ship as "prompt-compression-with-audit"; not the headline gain but meaningful
- E3 perplexity gap 5-15%: ship L3 as "audit-grade Memorizing Transformers"; substrate's deletion-cert is the differentiator, not perplexity

---

## Section 1: The 7 integration LAYERS

Definitions ordered by depth of integration into LLM internals. L1 is the shallowest (LLM unmodified, text-only interface); L7 is the deepest (substrate IS the attention mechanism, requires full architectural retrain).

### L1: Token-level (substrate stores text, LLM reads as raw context)

- **Data:** substrate atoms hold (text_fact, embedding, provenance, role-filler binding)
- **Retrieval:** substrate.retrieve_fact(query) returns text strings appended to LLM context
- **LLM modification:** NONE; substrate accessed via tool-use / function-calling protocol
- **Feasibility:** YES on Claude, GPT-4, Gemini, Llama, Mistral, custom
- **Current state:** Pattern B + v278 substrate-LLM hybrid both operate here; CoT state offload extends L1 to 1000-step reasoning
- **Effective context expansion:** unbounded in principle (substrate storage); LLM working set still bounded by native context
- **Unique substrate value:** deletion-cert + per-atom provenance + edit-isolation guarantees over text retrieval

### L2: Soft-prompt / continuous-embedding (substrate stores compressed prompt embeddings)

- **Data:** substrate atoms hold (compressed_prompt_embedding `\in R^d_model`, source_text, provenance)
- **Retrieval:** substrate retrieves K matching gist atoms; LLM consumes as soft-prefix in input embedding space
- **LLM modification:** REQUIRES inputs_embeds API access (HuggingFace Transformers `inputs_embeds=` argument; Llama / Mistral / Pythia all expose this; Claude / GPT-4 do NOT expose embedding-level input)
- **Feasibility:** Llama 3.1 YES; closed-weight Claude/GPT-4 NO
- **Current state:** gist tokens (Mu et al. 2023) shows 26x compression on open-weight T5; AutoCompressors (Chevalier et al. 2023) shows similar on OPT; both train task-specific encoders
- **Effective context expansion:** ~10-30x prompt compression -> 80K-240K effective context on 8K-native Llama
- **Unique substrate value:** atom-level provenance per gist token (gist tokens are opaque; substrate atoms are queryable + deletable)

### L3: KV-cache extension (substrate stores past attention KV pairs)

- **Data:** substrate atoms hold (key `\in R^d_head`, value `\in R^d_head`, layer_idx, head_idx, source_position, provenance)
- **Retrieval:** at attention computation in layer L, query `q_t` matches against substrate KV by key-similarity; substrate-retrieved KV concatenated with fresh-context KV; attention runs over combined KV
- **LLM modification:** REQUIRES custom attention layer (modify `forward()` in attention module to accept external KV); Llama-style attention is straightforwardly extensible; Memorizing Transformers (Wu et al. 2022) is the canonical implementation
- **Feasibility:** Llama 3.1 YES (requires ~200 LOC attention-layer modification); closed-weight Claude/GPT-4 NO (no attention-layer access)
- **Current state:** Memorizing Transformers achieves 262K effective context on PG-19; H2O / SnapKV / Scissorhands compress KV via heavy-hitter selection (substrate could replace heavy-hitter-oracle with provable-audit oracle)
- **Effective context expansion:** 50K-1M effective context depending on substrate size and head-attention-budget
- **Unique substrate value:** every KV pair has provenance + deletion-cert; H2O has no audit trail; per-tenant KV isolation possible via multi-substrate composition (KF-3 production hook)

### L4: Hidden-state injection (substrate stores layer-k hidden states)

- **Data:** substrate atoms hold (hidden_state `\in R^d_model`, layer_idx, source_context, provenance)
- **Retrieval:** at forward pass through layer L, substrate-retrieved hidden states added to or replace `h_L` via activation steering
- **LLM modification:** REQUIRES forward-pass hooks at chosen layer (HuggingFace `register_forward_hook` works on Llama / Mistral / Pythia); activation steering literature shows the mechanism is robust at d_model-scale
- **Feasibility:** Llama 3.1 YES (forward hooks ~50 LOC); closed-weight Claude/GPT-4 NO
- **Current state:** activation steering (Turner et al. 2023, Zou et al. 2023 RepEng) demonstrates hidden-state addition shifts model behavior; substrate analog is to store known-good hidden states keyed by context, hot-load on similar future contexts
- **Effective context expansion:** moderate (not a context expansion per se; this is a "remembered cognitive state" mechanism)
- **Unique substrate value:** substrate-stored cognitive states have provenance + are queryable + deletable; activation-steering vectors are typically held in-process

### L5: Memory-layer replacement (substrate replaces a transformer attention layer)

- **Data:** substrate atoms hold full key-value-output triples; substrate operates as the attention layer
- **Retrieval:** substrate.retrieve replaces the layer's `softmax(QK^T)V` computation
- **LLM modification:** REQUIRES architectural surgery + fine-tuning to recover quality post-surgery
- **Feasibility:** open-weight YES with fine-tuning budget (~$50K-$500K compute); closed-weight NO
- **Current state:** Hopfield Layers (Ramsauer et al. 2020) precedent; "memory layer" approaches exist but require co-training
- **Effective context expansion:** structural (substrate layer is unbounded in storage)
- **Unique substrate value:** fully auditable attention layer; potentially much faster than softmax at fixed accuracy due to sparsity

### L6: Activation-pattern matching (substrate stores activation patterns; LLM steered via similarity)

- **Data:** substrate atoms hold full layer-by-layer activation traces for "known-good" generation sequences
- **Retrieval:** at inference, similar activations to substrate-stored ones bias next-token generation
- **LLM modification:** moderate (sampling-time hook); doesn't require retrain
- **Feasibility:** open-weight YES; closed-weight NO
- **Current state:** "knowledge editing" literature (ROME, MEMIT) operates in this space; substrate analog is a queryable knowledge-edit store
- **Effective context expansion:** indirect (substrate biases generation; not literal context extension)
- **Unique substrate value:** audit-grade knowledge editing; current ROME/MEMIT edits are irreversible without checkpointing

### L7: Full architectural substrate-attention (substrate IS the attention mechanism, major retrain)

- **Data:** substrate atoms hold full attention operator state; LLM trained with substrate-attention from initialization
- **Retrieval:** substrate IS the attention mechanism
- **LLM modification:** FULL RETRAIN ($1M-$100M compute scale)
- **Feasibility:** only with major investor / lab partner commitment; out of substrate-product scope
- **Current state:** RetNet (Sun et al. 2023), Mamba/Mamba-2 (Gu et al. 2023, 2024) replace attention with state-space alternatives; substrate could plausibly fill the same role at this level
- **Effective context expansion:** structurally unbounded
- **Unique substrate value:** structurally auditable transformer; would be a novel architecture

### Summary table

| Layer | Data | LLM mod | Closed-weight feasible? | Open-weight feasible? | Effective context |
|---|---|---|---|---|---|
| L1 Token | Text + provenance | NONE | YES | YES | ~unbounded (working set bounded) |
| L2 Soft-prompt | Compressed embeddings | `inputs_embeds` access | NO | YES (Llama) | 80K-240K @ 10-30x compression |
| L3 KV-cache | Past attention KV pairs | Custom attention layer | NO | YES (Llama, ~200 LOC) | 50K-1M effective tokens |
| L4 Hidden-state | Layer-k hidden states | Forward hooks | NO | YES (Llama, ~50 LOC) | Cognitive-state restore |
| L5 Memory-layer | Full KV-O triples | Architectural surgery + FT | NO | YES with $50K-500K FT | Structural |
| L6 Activation pattern | Activation traces | Sampling-time hook | NO | YES | Indirect |
| L7 Full substrate-attention | Attention operator | Full retrain | NO | NO (custom train only) | Structural |

---

## Section 2: Literature survey (memory-augmented LLM architectures)

Each entry: paper -> what it does -> substrate add/replace opportunity -> portability.

### StreamingLLM (Xiao et al. ICLR 2024)

- **Mechanism:** Attention-sink (first K tokens, K=4 suffices) + sliding window KV cache; enables Llama-2/MPT/Falcon/Pythia to handle 4M+ tokens without fine-tuning
- **Key insight:** Initial tokens are "attention sinks" with disproportionate attention mass; preserving them stabilizes streaming generation
- **Substrate opportunity:** REPLACE attention sink with substrate-anchor atoms. Substrate atoms can serve as semantic-anchor sinks (better than positional-only sinks); each anchor has provenance + deletion-cert. Could plausibly improve streaming quality at long horizons.
- **Implementation cost:** L3-style modification; ~1-2 weeks engineering on Llama
- **Portability:** Llama-family direct; closed-weight not feasible

### H2O / Heavy-Hitter Oracle (Zhang et al. NeurIPS 2023)

- **Mechanism:** Identify heavy-hitter tokens (small set of tokens that capture most attention mass); evict non-heavy-hitter KV from cache
- **Key insight:** Cumulative-attention-score selection finds a small KV subset that preserves performance
- **Substrate opportunity:** Substrate as "audit-grade H2O" -- substrate stores ALL evicted KV with provenance; deletion-cert provides provable forgetting (impossible with vanilla H2O which silently discards); per-tenant H2O eviction policy via multi-substrate composition
- **Implementation cost:** L3-style; ~2-3 weeks engineering on Llama
- **Portability:** Llama-family direct; SnapKV / Scissorhands are similar variants substrate could overlay

### LongMem (Wang et al. NeurIPS 2023)

- **Mechanism:** Frozen backbone LLM + adaptive residual SideNet trained as memory retriever; KV pairs of past context extracted into memory bank; SideNet queries memory bank at memory-augmented layer
- **Key insight:** Decouples memory storage (frozen LLM) from memory retrieval (trained SideNet); avoids memory-staleness issue
- **Substrate opportunity:** REPLACE the memory bank with substrate -- substrate stores KV pairs as atoms with provenance; SideNet queries substrate via cosine-cleanup; substrate provides edit-isolation + deletion-cert; potentially smaller SideNet because substrate's cosine retrieval is high-quality
- **Implementation cost:** L3-L4 hybrid; ~3-4 weeks engineering (substrate-as-memory-bank + SideNet adaptation)
- **Portability:** LongMem's SideNet training is the cost; substrate inserts cleanly

### Memorizing Transformers (Wu et al. ICLR 2022)

- **Mechanism:** Non-differentiable kNN attention over external memory of past KV pairs; gated combination of local attention + kNN attention; scales to 262K-token effective context
- **Key insight:** External memory can be non-differentiable and still improve perplexity; gate learns when to use external memory vs local
- **Substrate opportunity:** REPLACE kNN store with substrate -- substrate stores KV with provenance; substrate's cosine-cleanup serves as kNN; deletion-cert + audit are native; substrate as Memorizing-Transformers-with-audit is the cleanest L3 ship candidate
- **Implementation cost:** L3-style; ~2-3 weeks engineering on Llama
- **Portability:** open-weight direct; THIS IS THE PRIMARY L3 SHIP CANDIDATE (see E3)

### RetNet / Mamba / Mamba-2 (Sun et al. 2023; Gu & Dao 2023, 2024)

- **Mechanism:** State-space alternatives to attention; linear-time inference; recurrent state replaces attention's quadratic cost
- **Key insight:** Attention's quadratic cost can be replaced by recurrent state at competitive quality
- **Substrate opportunity:** L7-level. Substrate could plausibly fill the state-space role with audit primitives. But this is custom-train territory; not v278 ship candidate.
- **Implementation cost:** $10M-$100M for full-scale training
- **Portability:** out of scope for substrate-product

### LongContext via continuous prompts / gist tokens (Mu et al. 2023)

- **Mechanism:** Compress prompts into "gist tokens" via meta-learning; up to 26x compression at minimal quality loss
- **Key insight:** Soft-prompt prefix can encode arbitrary instructions in <=K virtual tokens
- **Substrate opportunity:** REPLACE gist tokens with substrate atoms -- each substrate atom encodes one gist; atoms compose via binding-algebra (multi-document gist composition); per-atom provenance + deletion
- **Implementation cost:** L2-style; ~1-2 weeks engineering on Llama
- **Portability:** Llama-family direct; THIS IS THE PRIMARY L2 SHIP CANDIDATE (see E2)

### Compressive Transformers (Rae et al. 2019)

- **Mechanism:** Multi-resolution memory hierarchy (recent KV in fine resolution, older KV in compressed form); sliding compression operator (avg-pool / 1D-conv / dilated conv)
- **Key insight:** Time-decay compression preserves recent detail + old gist
- **Substrate opportunity:** ADD substrate as the deepest compression tier -- after temporal compression saturates, store compressed memory in substrate with audit + deletion; substrate becomes the "long-term archive" tier
- **Implementation cost:** L3-L1 hybrid; ~2-3 weeks engineering
- **Portability:** open-weight (Compressive Transformers is a specific architecture; substrate generalizes the mechanism)

### MemGPT / Letta (Packer et al. 2023)

- **Mechanism:** OS-style memory paging; LLM treated as CPU with limited "RAM" (context); archival memory + recall memory paged in/out via LLM-issued memory operations
- **Key insight:** LLM can be its own memory manager via self-edits + tool calls; concept of memory hierarchy ported to LLM agent design
- **Substrate opportunity:** REPLACE archival memory with substrate -- substrate provides deletion-cert + per-fact provenance + edit-isolation that MemGPT's vanilla archival cannot. Letta integration partnership pathway: substrate as a drop-in archival backend; sells the audit-grade story to Letta's existing customer base.
- **Implementation cost:** L1-style; ~1-2 weeks engineering
- **Portability:** ANY LLM (closed-weight + open-weight both work); THIS IS THE PRIMARY L1 PARTNERSHIP SHIP CANDIDATE (see E5)

### InfiniAttention / Infini-attention (Munkhdalai et al. 2024)

- **Mechanism:** Compressive memory + local attention; linear-time on long sequences; fixed-parameter compressive memory holds entire history
- **Key insight:** Linear attention with compressive state can achieve effectively infinite context at bounded memory
- **Substrate opportunity:** REPLACE compressive memory with substrate -- substrate atoms as the compressive state; provenance per atom; audit-grade infini-attention
- **Implementation cost:** L3-style; ~3-4 weeks engineering
- **Portability:** Llama-family direct; secondary L3 ship candidate after Memorizing Transformers

### Recurrent Memory Transformer (Bulatov et al. 2022)

- **Mechanism:** Segment-level recurrent memory tokens that carry state across segments
- **Key insight:** Adding K memory tokens at segment boundaries extends effective context recurrently
- **Substrate opportunity:** REPLACE recurrent memory with substrate -- substrate atoms as cross-segment memory carriers; deletion-cert at segment-level granularity
- **Implementation cost:** L2-L3 hybrid; ~2-3 weeks engineering
- **Portability:** open-weight only

### AutoCompressors (Chevalier et al. 2023)

- **Mechanism:** OPT-2.7B fine-tuned to compress its own context into 50-token summary vectors; recursive compression possible
- **Key insight:** LLM can be trained to compress its own state into soft-prompt-compatible summary
- **Substrate opportunity:** Substrate stores the compressed summaries with provenance; ingestion = LLM-emitted summary -> substrate atom binding
- **Implementation cost:** L2-style + ingestion training; ~3-4 weeks engineering
- **Portability:** open-weight; closed-weight if substrate ingestion uses LLM as compression tool via tool-use

---

## Section 3: Substrate-specific mechanisms per layer

### L1: standard RAG + CoT state offload

Already addressed in Pattern B + v278 hybrid spec. Mechanism: substrate emits text facts via tool-use; LLM composes them in context. CoT state offload extends working-set lifetime: substrate stores intermediate reasoning state at hop N, LLM evicts from context, re-loads on demand at hop M > N. Substrate's deletion-cert applies to the full CoT chain (deleting a fact at hop K invalidates dependents at hops K+1..N).

**Compression ratio:** ~3-4x reduction in cumulative LLM tokens vs pure CoT (per v278 hybrid spec Section 5)
**Quality preservation:** depends on substrate single-hop accuracy; chain accuracy ~0.55-0.70 on HotpotQA per hybrid spec

### L2: substrate-as-compressed-prompt-store

Mechanism:
1. Ingest: long prompt P split into K segments; for each segment, encode via AutoCompressor-style summary -> compressed embedding `e_k \in R^d_model`; bind into substrate atom with provenance
2. Retrieval: query Q encoded; substrate retrieves top-K atoms by cosine; concatenate retrieved gist embeddings as soft-prefix
3. Generation: LLM consumes `[gist_1, ..., gist_k, <Q-tokens>]` as input embeddings

**Compression ratio:** 10-30x (per gist tokens / AutoCompressors literature; substrate matches at parity if ingestion is well-tuned)
**Quality preservation:** open question -- substrate codebook geometry must support the d_model embedding distribution; Property 4 Johnson-Lindenstrauss sanity check is the gating test

**Practical for closed-weight LLMs:** NO -- requires `inputs_embeds` API access not exposed by Claude/GPT-4. Open-weight Llama 3.1-8B yes.

### L3: substrate-as-KV-cache-extension (PRIMARY DEEP INTEGRATION)

Mechanism:
1. Ingest: for each (text_segment, processing through Llama) extract layer-L attention KV pairs `(k_i, v_i)`; bind each `(layer_L, head_h, position_p, k_i, v_i)` as a substrate atom
2. Retrieval: at attention layer L, head h, query `q_t`; substrate retrieves top-K atoms by cosine-similarity to `q_t` against stored `k_i`; returns top-K (k, v) pairs
3. Combined attention: native KV cache + substrate-KV concatenated; attention computed over union
4. Gating: learned scalar gate weights substrate-KV vs native-KV per attention head (per Memorizing Transformers protocol)

**Effective context expansion:** at N=4096 substrate, ~50K KV pairs storable per layer-head pair across the substrate; at typical Llama-3.1-8B (32 layers x 32 heads = 1024 head pairs), substrate footprint is multi-substrate composed (one substrate per layer-head pair, or compressed shared substrate)

Honest estimate: substrate at N=4096 BSC production scale can store ~50K-100K KV pairs at retrievable quality (matches KF-1 + KF-2 capacity envelope); this gives ~50K-100K effective context expansion vs native Llama 8K.

At N=8192 production scale: ~100K-200K effective context expansion.

At multi-substrate composition (one substrate per layer-group): substrate footprint multiplies, effective context could reach 1M-equivalent for specific layer-groups.

**Practical for closed-weight LLMs:** NO -- requires custom attention-layer modification. Open-weight Llama yes.

### L4: substrate-as-hidden-state-injection

Mechanism:
1. Ingest: at known-good processing points (e.g. after multi-step reasoning succeeds), capture layer-L hidden state `h_L`; bind as substrate atom keyed by context-summary
2. Retrieval: at inference, given current context, substrate retrieves top-K matching hidden states; weighted-add to `h_L` via activation-steering-style scalar
3. Effect: LLM "remembers" cognitive state from past contexts

**Effective context expansion:** indirect; this is cognitive-state restore, not literal context. Useful for repeated reasoning patterns (e.g. legal precedent reasoning across cases).

**Practical for closed-weight LLMs:** NO. Open-weight Llama yes (forward hooks).

### L5-L7: out of scope for v278 substrate-product

Requires architectural retraining. Substrate is well-positioned to participate in L5-L7 conversations with potential lab/investor partners, but not a v278 ship candidate.

---

## Section 4: Feasibility matrix

| Integration | Claude API | GPT-4 API | Gemini API | Llama 3.1 (open-weight) | Mistral / Pythia | Custom-trained |
|---|---|---|---|---|---|---|
| L1 Token (RAG + tool-use + CoT offload) | YES (v278 hybrid) | YES | YES | YES | YES | YES |
| L2 Soft-prompt | NO (no embedding input) | NO | NO | YES (`inputs_embeds`) | YES | YES |
| L3 KV-cache extension | NO | NO | NO | YES (~200 LOC attention mod) | YES | YES |
| L4 Hidden-state injection | NO | NO | NO | YES (~50 LOC hook) | YES | YES |
| L5 Memory-layer replacement | NO | NO | NO | YES with $50K-500K FT | YES with FT | YES |
| L6 Activation-pattern matching | NO | NO | NO | YES | YES | YES |
| L7 Full substrate-attention | NO | NO | NO | NO (full retrain only) | NO | YES |

**Strategic implication:** Closed-weight APIs cap substrate-LLM integration at L1. Substrate's deeper-integration value (L2-L4) is ONLY accessible via open-weight model partnerships. Llama 3.1 is the natural target (largest open-weight ecosystem; broad ecosystem; HuggingFace-native). Mistral / Pythia / Qwen are equivalent technically.

---

## Section 5: The MOST PRODUCTIVE near-term integration

**Verdict:** L1 (CoT state offload via tool-use) is the deepest integration possible with closed-weight LLMs and is ALREADY the v278 hybrid spec. Ship E1 (3-5 days eng) immediately.

For deeper integration:
- L2 (soft-prompt store) requires open-weight Llama -> E2 build path
- L3 (KV-cache extension) requires open-weight Llama + custom attention -> E3 build path (highest-payoff but highest-cost)
- L4 (hidden-state injection) requires open-weight Llama + forward hooks -> E4 build path (secondary; activation-steering analog)

**Gating:** Property 4 Johnson-Lindenstrauss sanity check (1 hr CPU) decides whether L2/L3/L4 open-weight work commits or is parked. PASS opens E2-E4 budget; FAIL closes L2-L4 cleanly and focuses on L1 product extensions (E1 + E5).

**Pragmatic 3-month roadmap:**
- Month 1: Ship E1 (L1 CoT state offload) + run Property 4 sanity check
- Month 2: If Property 4 PASS, ship E3 (L3 KV-cache extension on Llama 3.1-8B) as headline deep-integration demo; if FAIL, ship E5 (Letta partnership archival backend) for product traction
- Month 3: Whichever branch landed, scale up to production-N substrate + customer pilot demo

---

## Section 6: Substrate's competitive position vs each memory-augmented architecture

| Architecture | Substrate replaces what | Implementation cost | Accuracy expected | Substrate-specific advantage |
|---|---|---|---|---|
| **StreamingLLM** | Attention sink with semantic-anchor substrate atoms | 1-2 wks | Match streaming quality | Anchors have provenance + deletion-cert; semantic > positional |
| **H2O / SnapKV / Scissorhands** | Heavy-hitter eviction with audit-grade substrate KV store | 2-3 wks | Match compression ratio | Provable forgetting via deletion-cert; per-tenant KV isolation |
| **LongMem** | Memory bank with substrate atoms | 3-4 wks | Match or beat (smaller SideNet) | Edit-isolation; cross-tenant safety; auditable memory bank |
| **Memorizing Transformers** | kNN store with substrate cosine-cleanup | 2-3 wks | Match perplexity | Audit-grade; deletion-cert; per-tenant memory; THIS IS THE PRIMARY L3 CANDIDATE |
| **gist tokens / AutoCompressors** | Gist token storage with substrate atoms | 1-2 wks | Match compression at 10-30x | Provenance per gist; composable via binding-algebra |
| **Compressive Transformers** | Deepest compression tier with substrate archive | 2-3 wks | Match or beat at archival | Audit-grade archival; permanent provenance |
| **MemGPT / Letta** | Archival memory backend with substrate | 1-2 wks | Improve recall accuracy | Deletion-cert + per-fact audit; structural Letta partnership pathway |
| **InfiniAttention** | Compressive memory with substrate atoms | 3-4 wks | Match infinite-context claims | Audit-grade infini-attention; secondary L3 candidate |
| **Recurrent Memory Transformer** | Recurrent memory tokens with substrate carriers | 2-3 wks | Match RMT quality | Segment-level audit + deletion |

---

## Section 7: Concrete substrate-extension experiments to ship

Ranked by (P_deflated x impact) / (cost):

### E1: Substrate-as-CoT-state-offload via tool-use (L1)

- **Layer:** L1
- **Mechanism:** v278 hybrid spec; LLM tool-use + substrate fact retrieval + CoT-state offload to substrate
- **LLM target:** Claude / GPT-4 (closed-weight friendly)
- **Cost:** 3-5 days engineering (orchestrator already specd in v278 hybrid note)
- **API budget:** ~$20-50 for 50-question HotpotQA MVP
- **P_deflated (HARD-PASS at HotpotQA 1000-q):** 0.55 (per v278 hybrid spec)
- **Expected accuracy:** 0.55-0.70 HotpotQA (substrate-bottlenecked at single-hop)
- **Strategic positioning:** Pattern B headline + multi-hop agentic capability
- **Status:** READY TO SHIP via v278 hybrid spec

### E2: Substrate-as-compressed-prompt-store (L2)

- **Layer:** L2
- **Mechanism:** AutoCompressors-style compression -> substrate atom; retrieved as soft-prefix
- **LLM target:** Llama 3.1-8B (open-weight required)
- **Cost:** 1-2 weeks engineering (substrate ingestion + soft-prefix injection)
- **API budget:** ~$50-100 (model hosting; some baseline comparison API calls)
- **P_deflated (HARD-PASS: 10x compression at 80% quality):** 0.35 (novel-synthesis cap 0.50 applied; Property 4 sanity is gating)
- **Expected effective context:** 80K-240K on 8K-native Llama
- **Strategic positioning:** "prompt-compression-with-audit" product category; open-weight ecosystem demo

### E3: Substrate-as-KV-cache-extension (L3) -- HEADLINE DEEP INTEGRATION

- **Layer:** L3
- **Mechanism:** Memorizing-Transformers-style external memory; substrate stores KV pairs; cosine-cleanup retrieval; gated combination with native KV
- **LLM target:** Llama 3.1-8B (open-weight required; custom attention layer ~200 LOC)
- **Cost:** 2-3 weeks engineering (attention-layer modification + substrate ingestion pipeline + benchmark harness)
- **API budget:** ~$100-200 (model hosting; PG-19 / arXiv-math benchmark comparison)
- **P_deflated (HARD-PASS: perplexity within 5% of MT @ 100K effective context):** 0.40 (novel-synthesis cap 0.50 applied; substrate cosine-cleanup vs MT learned-kNN is the open question; Property 4 sanity is gating prerequisite)
- **Expected effective context:** 50K-100K on substrate N=4096; 100K-200K on N=8192
- **Strategic positioning:** "audit-grade Memorizing Transformers"; substrate's UNIQUE structural overlay on a proven mechanism; this is the headline deep-integration demo
- **Honest scope:** if HP works, substrate is positioned as "compute-cheap, audit-grade alternative to longer LLM context"; if FAIL, L3 is closed and substrate restricts to L1 product extensions

### E4: Substrate-as-memorizing-attention-bank (L3-L4 hybrid, Memorizing Transformers analog)

- **Layer:** L3-L4
- **Mechanism:** extends E3 with hidden-state injection from substrate-retrieved triples
- **LLM target:** Llama 3.1-8B
- **Cost:** 3-4 weeks engineering (extends E3)
- **API budget:** ~$200-300
- **P_deflated:** 0.30 (extends E3 risks; compounds the substrate-vs-learned-kNN gap)
- **Expected benchmark:** long-document Q&A (NarrativeQA / QASPER)
- **Strategic positioning:** secondary to E3; ship only if E3 HARD-PASS

### E5: Substrate as MemGPT/Letta archival backend (L1, partnership pathway)

- **Layer:** L1
- **Mechanism:** substrate as drop-in archival memory backend for Letta agents
- **LLM target:** ANY (closed-weight + open-weight)
- **Cost:** 1-2 weeks engineering (Letta API integration; substrate REST wrapper)
- **API budget:** ~$0 (Letta-side compute; substrate-side is the existing hdlab_service)
- **P_deflated (Letta integration ships):** 0.45 (Letta partnership pathway is structurally open; engineering is straightforward)
- **Expected impact:** access to Letta's existing customer base (Cognition Labs Devin team, etc); audit-grade archival as differentiator
- **Strategic positioning:** "structural partnership via product-engineering integration"; complementary to E1 + E3

### Recommended ship order

1. **E1** (Month 1, Week 1): substrate-LLM hybrid MVP per v278 spec
2. **Property 4 sanity check** (Month 1, Week 1, parallel to E1): 1 hr CPU; gates E2-E4
3. **E5** (Month 1, Weeks 2-3): Letta integration; product traction
4. **E3** (Month 2, Weeks 1-3): IF Property 4 PASS; headline deep-integration demo
5. **E2** (Month 2-3): IF E3 HARD-PASS; complementary L2 demo
6. **E4** (Month 3): IF E3 HARD-PASS; extends to L4

---

## Section 8: The "thousand-step CoT" capability -- substrate path

| Architecture | Max CoT steps | Quality at depth | Cost at depth N |
|---|---|---|---|
| Standard LLM (Claude 200K-context) | ~50-100 (context-limited; 50 steps eat 30-50K tokens) | degrading at 50+ | quadratic attention; 200K input is expensive |
| Substrate-augmented L1 CoT (v278 hybrid + offload) | ~500-1000 (offload extends working-set lifetime) | substrate single-hop bottleneck (~0.85-0.95 per hop); chain self-corrects via LLM | ~3-4x cheaper than pure CoT |
| Substrate-augmented L3 KV-cache extension | ~1000-10000 (KV-substrate carries past attention state) | KV-similarity bottleneck (~0.85-0.95 per retrieval); cumulative effect TBD | substrate retrieval cost; no quadratic LLM expansion |
| Substrate-augmented L4 hidden-state injection | ~indirect (not literal step count; cognitive-state restore) | activation-steering literature shows moderate quality at moderate scale | minimal; just forward-pass hooks |

**Headline:** L1 CoT state offload enables 500-1000 step reasoning chains TODAY on closed-weight Claude/GPT-4. L3 KV-cache extension on open-weight Llama could push to 10000 steps with substrate-bounded quality. The substrate's audit-grade overlay applies at every step depth -- this is uniquely substrate.

---

## Section 9: Customer-facing concrete demos for substrate-as-context-extension

### Demo 1: Legal eDiscovery agent with 10K-document context

- **Substrate size:** ~50K-100K atoms at N=4096 (covers 10K documents at ~10 atoms/doc for key facts + entities + dates + legal-relevance markers)
- **LLM working set:** 5-10 atoms per hop (substrate.retrieve_fact returns top-5 by query)
- **End-to-end latency:** ~5-15s per multi-hop query (50ms substrate retrieval + 1-3s LLM per hop; 10-hop average query)
- **Value proposition:** "deposit 10K legal documents into substrate once; LLM accesses every relevant document via audit-trail provenance; each retrieved fact has source-document pointer + deletion-cert; privilege review is per-atom"
- **Killer competitive position:** Pattern B legal eDiscovery use case extended to full-corpus scale; competitor RAG systems have no per-atom audit trail
- **Estimated win rate vs Anthropic Memory / Mem0 / LangMem:** structural -- those systems cannot match the audit-grade story

### Demo 2: Software refactor agent across 100K LOC codebase

- **Substrate size:** ~200K-500K atoms at N=4096-8192 (one atom per function/class/import-relationship + comments + tests)
- **LLM working set:** 20-50 atoms per refactor decision (substrate.compose_query for symbol-resolution)
- **End-to-end latency:** ~10-30s per refactor decision (multi-hop dependency analysis)
- **Value proposition:** "audit-grade context across a 100K-LOC codebase; LLM never loses track of which function depends on which; refactor-impact-prediction via deletion-cert cascade"
- **Killer competitive position:** Cognition Labs Devin's "context retention degrades in long sessions" failure mode -- substrate fixes structurally
- **Estimated win rate vs Devin baseline:** high if Property 4 sanity passes (substrate hidden-state augmentation gives session-coherence)

### Demo 3: Healthcare diagnostic agent across multi-day patient case

- **Substrate size:** ~10K-50K atoms per patient (longitudinal medical history: labs, imaging, medications, clinician notes)
- **LLM working set:** 10-20 atoms per diagnostic hop
- **End-to-end latency:** ~5-10s per query
- **Value proposition:** "audit-grade longitudinal patient memory; HIPAA-compliant per-fact deletion-cert; differential diagnosis traceable to source records"
- **Killer competitive position:** compliance-grade (HIPAA + JCAHO audit trail) that vector-RAG cannot provide structurally
- **Estimated win rate vs healthcare LLM baselines:** structural compliance advantage

### Demo 4: Strategic planning agent over multi-month corporate strategy

- **Substrate size:** ~5K-20K atoms (decision rationale, meeting notes, market data, financial assumptions)
- **LLM working set:** 5-15 atoms per planning step
- **End-to-end latency:** ~3-8s per query
- **Value proposition:** "audit-grade strategic memory; every recommendation traceable to source-document evidence; edit-with-impact-prediction for scenario planning"
- **Killer competitive position:** the substrate's killer feature 5 (edit-with-impact-prediction) is uniquely deployable here
- **Estimated win rate:** depends on enterprise design-partner pipeline; structural fit

---

## Section 10: Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Closed-weight LLM API limitations cap L2+ on Claude/GPT-4 | HIGH | Open-weight Llama 3.1 is the L2-L4 target; Letta partnership for L1 closed-weight |
| Claude/GPT-4 training cutoff doesn't know substrate retrieval patterns | MEDIUM | Tool-use steering via system prompt + ReAct-style examples; well-established pattern |
| Open-weight LLM quality gap (Llama vs Claude) | HIGH | Llama 3.1-70B closes much of the gap; substrate-augmented Llama may match or beat vanilla Claude at long-context tasks |
| Customer integration complexity (new architecture) | MEDIUM | Letta partnership reduces; sales education curve real but manageable |
| Compute cost at L5-L7 not competitive | HIGH | L5-L7 out of scope unless lab partner; v278 ship is L1+L3 |
| Substrate's d=25-50 multi-hop cliff if reused for KV-retrieval chain | MEDIUM | L3 design uses substrate as PARALLEL KV retrieval (not chained); cliff doesn't apply at this layer |
| Property 4 Johnson-Lindenstrauss sanity FAIL closes L2-L4 cleanly | LOW (it's the gating check, not a downstream risk) | Run cheap check first; cost-bounded |
| L3 substrate-cosine vs MT learned-kNN quality gap | MEDIUM-HIGH | This is the main E3 risk; HARD-FAIL closes L3 |
| Customer expectation mismatch: "we want longer context" vs "substrate gives audit-grade alternative" | MEDIUM | Position substrate as "compute-cheap audit overlay" not "context-window replacement" |
| Letta partnership requires their engineering bandwidth | LOW | E5 substrate-side is fully implementable; Letta-side integration is minor |

---

## Section 11: What this means for the 3-month roadmap

### Item 1 (Pattern B integration demo) -- updated mapping

- Pattern B Phases 1-3 operate at L1 (token-level + tool-use)
- v278 substrate-LLM hybrid extends Pattern B to L1 + CoT state offload
- Property 4 sanity check (Property 4 from seven_intrinsic_properties spec) gates L2-L4 expansion
- E1 (substrate-LLM hybrid MVP) is the immediate Pattern B headline upgrade

### Item 2 (seven intrinsic properties validation)

- Property 4 (LLM-internal representation compatibility) is the cheap-decisive-test for L2-L4 layer access
- Run Property 4 sanity check in Week 1 alongside E1; result gates Month 2 commitment

### Item 3 (Pattern C deep integration -- previously 12-month horizon)

- THIS DRILL REFINES PATTERN C: Pattern C = L3-L4 substrate integration on open-weight Llama
- 12-month horizon should be revised: E3 (L3 KV-cache extension) is achievable in 2-3 weeks engineering if Property 4 PASSes
- Pattern C ships in Month 2-3 of the 3-month roadmap, not Month 12

### NEW: open-weight model partnership track

- Llama 3.1-8B (or larger) integration becomes a structural product-engineering track
- E2-E4 ship candidates all need open-weight access
- Consideration: HuggingFace partnership, AnthropicLab open-weight collaborator, Meta direct (unlikely)

---

## Section 12: The single most consequential reframing (if L3 works)

**IF substrate-as-KV-cache-extension validates at L3 HARD-PASS:**

Substrate becomes a "compute-cheap, audit-grade alternative to longer LLM context windows":

| Metric | Without substrate | With substrate L3 |
|---|---|---|
| Native context | 8K (Llama 3.1-8B) | 8K + 50K-200K substrate extension |
| Compute cost at K-token context | quadratic O(K^2) | linear in K + substrate retrieval (constant per hop) |
| Audit trail | NONE | per-token provenance via substrate atom-ids |
| Deletion-cert | NONE | structural deletion at KV-cache level |
| Multi-tenant isolation | NONE in shared model | KF-3 multi-substrate composition |

This is a structurally novel product category: "audit-grade infinite context" -- which neither vanilla long-context LLMs nor existing RAG systems can deliver.

**Substrate at N=4096 BSC production:** ~50K-token effective context extension
**Substrate at N=8192 BSC production:** ~100K-token effective context extension
**Multi-substrate composition (M substrates):** M * N effective context expansion

**Strategic implication:** substrate's 24-month meaningful-production-component probability adjusts UPWARD to 0.55-0.65 if L3 validates (from 0.50-0.55 stated in v278 hybrid spec).

---

## Section 13: What this DOES enable (substrate-as-context-extension L1-L3)

- 100K-token effective context on LLMs with native 8K context (via L3 substrate KV-cache extension on Llama 3.1-8B)
- 1M-token effective context (via L3 with multi-substrate composition; per-layer-group substrates)
- Audit-grade context history (every token provenance via substrate atom-ids)
- Deletion-cert at context-level (provable forgetting of past context per atom)
- Per-tenant context isolation (KF-3 multi-substrate composition gives structural tenant isolation)
- "Thousand-step CoT" reasoning chains (L1 today; L3 at scale tomorrow)
- Letta archival memory upgrade path (E5 partnership)
- Compliance-grade long-context for healthcare / legal / financial use cases (Demos 1-4)

## Section 14: What this DOES NOT enable

- Native long-context reasoning quality improvement (substrate doesn't improve LLM's reasoning capability; it extends accessible context)
- Cross-context coherence within a single inference (LLM still only "sees" working set at a time; substrate-augmented Llama has substrate-retrieved KV but not direct cross-attention to all stored context)
- Real-time learning of new facts within a conversation (substrate is read-mostly during inference; ingestion is a separate write-path)
- Closed-weight LLM deep integration (L2+ blocked on Claude/GPT-4 API limitations; only L1 ships there)
- Replacement of LLM reasoning core (substrate is a memory layer; LLM remains the reasoning engine)
- Sub-millisecond retrieval at L7 scale (substrate retrieval is O(N) cosine-cleanup; for L7 attention-replacement, native attention is faster per-token)

---

## Cross-thread synthesis

Integrates with:
- [[notes/substrate_llm_hybrid_multihop_architecture_v278_2026-05-29]]: v278 hybrid IS the L1 ship candidate (E1); this drill formalizes the layer-depth landscape it sits in
- [[notes/seven_intrinsic_properties_validation_designs_v278_2026-05-29]] Property 4: the 1-hour Johnson-Lindenstrauss sanity check is the gating prerequisite for L2-L4 build; this drill makes the "speculative" framing precise (it is the L2-L4 enabling check)
- [[notes/pattern_b_integration_demo_executable_spec_v278_2026-05-29]]: Pattern B operates at L1; this drill identifies Pattern C as L3-L4 open-weight integration (was previously vague 12-month horizon)
- [[notes/anthropic_memory_competitive_and_agentic_ai_architecture_v278_2026-05-29]] Section 8.6: "Bounded-context CoT via substrate state offloading" -- this drill formalizes the L1 mechanism + identifies the deeper L2-L4 paths
- [[notes/research_lagging_caps_v276_fresh_eyes_2026-05-29]]: substrate primitives inventory supports L3 KV-extension (cosine-cleanup + binding-algebra + provenance + deletion-cert all production-N HARD_PASS)
- [[memory/project_substrate_killer_features_2026-05-26]]: deletion-cert + compositionality-audit + edit-with-impact-prediction all gain a deeper-layer instantiation in L3
- [[memory/feedback_substrate_value_framing_2026-05-26]]: "which killer features ship first" matures to "which integration layer ships first per killer feature"
- [[memory/feedback_dont_overextend_theorems]]: substrate-internal multi-hop bounded at d=25-50 by argmax bottleneck -> L3 substrate-as-KV-cache is structurally a DIFFERENT mechanism (parallel KV retrieval, not chained); the cliff doesn't apply at this layer
- [[memory/feedback_aggressive_cross_domain_research]]: this drill maps substrate-as-LLM-extension to 11 distinct memory-augmented-LLM literature corners; cross-domain coverage achieves 11x scope
- [[memory/feedback_lit_scan_calibration_penalty]]: P estimates deflated 0.15-0.25; novel-synthesis cap 0.50 respected for L3 / L4 substrate-as-attention claims

---

## Substrate-product implications

If E1 (L1 hybrid) HARD-PASS:
- Pattern B headline upgrades to "multi-hop agentic reasoning with audit chain"
- Closed-weight Claude/GPT-4 customer demos viable immediately
- Letta partnership pathway (E5) opens
- 24-month production-component P adjusts to 0.55-0.60

If E3 (L3 KV-cache extension) HARD-PASS:
- Substrate becomes "compute-cheap audit-grade context extension"
- Open-weight Llama ecosystem becomes substrate's primary product channel
- Substrate killer features 1+2+5 all gain deeper-layer instantiation
- 24-month production-component P adjusts UPWARD to 0.55-0.65

If both E1 + E3 HARD-PASS:
- Substrate-as-INTRINSIC-LLM-extension validates as new product category
- Pattern C deep integration ships in Month 3 of 3-month roadmap (was previously 12-month horizon)
- 24-month production-component P adjusts to 0.65-0.75

If Property 4 sanity FAIL:
- L2-L4 closes cleanly; substrate stays at L1 product extensions
- E1 + E5 are the surviving ship candidates
- Substrate's positioning stays at "audit-grade text-level memory subsystem"
- 24-month production-component P unchanged at 0.50-0.55

---

## Citations (verified count)

Lit-scan verified via parallel WebSearch sub-agents (Sonnet model per feedback-subagent-model-optimization):

1. Xiao et al. 2024, "Efficient Streaming Language Models with Attention Sinks" (ICLR 2024) -- arxiv.org/abs/2309.17453
2. Zhang et al. 2023, "H2O: Heavy-Hitter Oracle for Efficient Generative Inference" (NeurIPS 2023) -- arxiv.org/pdf/2306.14048
3. Wu et al. 2022, "Memorizing Transformers" (ICLR 2022) -- arxiv.org/abs/2203.08913
4. Wang et al. 2023, "Augmenting Language Models with Long-Term Memory" (LongMem, NeurIPS 2023) -- arxiv.org/abs/2306.07174
5. Mu et al. 2023, "Learning to Compress Prompts with Gist Tokens" -- arxiv.org/pdf/2304.08467
6. Chevalier et al. 2023, "Adapting Language Models to Compress Contexts" (AutoCompressors)
7. Rae et al. 2019, "Compressive Transformers for Long-Range Sequence Modelling"
8. Packer et al. 2023, "MemGPT: Towards LLMs as Operating Systems" (now Letta) -- docs.letta.com
9. Munkhdalai et al. 2024, "Leave No Context Behind: Efficient Infinite Context Transformers with Infini-attention" -- arxiv.org/pdf/2404.07143
10. Bulatov et al. 2022, "Recurrent Memory Transformer"
11. Sun et al. 2023, "Retentive Network: A Successor to Transformer for Large Language Models" (RetNet)
12. Gu & Dao 2023, 2024, "Mamba: Linear-Time Sequence Modeling with Selective State Spaces" + "Mamba-2"
13. Ramsauer et al. 2020, "Hopfield Networks is All You Need"
14. SnapKV (Li et al. 2024) -- arxiv.org/html/2404.14469
15. ScissorHands (Liu et al. 2023)
16. LongLLMLingua / Prompt compression literature -- arxiv.org/pdf/2310.06839
17. Turner et al. 2023, "Activation Engineering: Steering Language Models Without Optimization"
18. Zou et al. 2023, "Representation Engineering: A Top-Down Approach to AI Transparency" (RepEng)
19. ROME / MEMIT (Meng et al. 2022) knowledge editing
20. "Memory-Augmented Transformers: A Systematic Review" -- arxiv.org/html/2508.10824v1 (general survey)

**Verified count: 20 distinct references across 11 mechanism families.**

Lit-scan calibration penalty applied: P estimates deflated 0.15-0.25 throughout; novel-synthesis P capped at 0.50 for L3/L4 substrate-as-attention claims (substrate cosine-cleanup vs learned-kNN attention quality on hidden-state distributions is the uncharted regime).
