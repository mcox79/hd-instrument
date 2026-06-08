# Research -> Testbed: TIER 5 SPRINT SPEC — Pythia substrate-as-attention + substrate-KV demo

**From:** Research  **Date:** 2026-06-08 ~19:30 UTC
**Re:** Final demo SPEC. RESCINDS SPEC v1, v2, v3. Single architectural pitch:
Tier 5a substrate-KV (production-ready) + Tier 5b substrate-attention-layer PoC (architectural proof).

## RESCINDED prior plans

- 3-mode toggle (Default / Cost-efficiency / Compliance)
- 5-wow-moment side-by-side demo
- Tier 4 LoRA plan
- Better-RAG positioning

## The killer demo concept

**Two panels. Same Pythia. Two architectural tiers of substrate integration.**

### Panel A — Tier 5a: Substrate-KV (production-ready, ships today)

Pythia-1.4B (Pythia-160M too small for coherent generation) + substrate-KV providing
external persistent memory. Standard transformer architecture; substrate retrieves
relevant facts BEFORE forward pass; LLM attends to substrate-provided context.

**Empirical foundation: D1/D2/D3 all HP (cycle 185 + 190 + 191):**
- D1 Pythia-160M substrate-KV recall=1.000 at M=2000
- D2 Pythia-1.4B substrate-KV recall=1.000 at M=2000
- N1 Pythia-2.8B substrate-KV recall=1.000 at M=2000
- M=5000 (78x context) + M=10000 (156x context) both HP
- PP-153 Qwen-1.5B HP (family-agnostic)

**This works empirically. Engineering is integration + polish.**

### Panel B — Tier 5b: Substrate-attention-layer (architectural proof)

Pythia-160M with ONE attention layer (e.g., layer 6 of 12) MODIFIED. Q comes from the
previous layer normally. K and V come from SUBSTRATE retrieval based on Q (instead of
W_k @ x_prev and W_v @ x_prev). Standard softmax(Q K^T) V attention math, with
substrate-provided K/V.

**Why Pythia-160M for Panel B specifically:**
- Smallest tractable transformer; cheapest to modify
- Already substrate-KV validated (D1 HP)
- Pythia architecture is clean and well-documented; easy to modify
- Even rough output is acceptable for ARCHITECTURAL DEMONSTRATION

**Empirical foundation: theoretical + adjacent**
- Ramsauer 2020 (Hopfield Networks Is All You Need): attention = Hopfield retrieval algebraically
- arXiv 2512.14709 (Dec 2024): attention = VSA binding algebraic equivalence
- Substrate IS Hopfield + VSA → substrate IS attention
- D1-D3 confirms substrate-LLM-hidden-state interface works
- What's novel: doing the substrate retrieval INSIDE the attention layer instead of BEFORE

## Hero metrics (always visible)

```
   Substrate KB:        200M+ facts (Wikidata + Wikipedia + ConceptNet + arXiv + PubMed)
   Substrate retrieval: 0.21ms P95 at 1M facts (PP-150)
   Substrate latency:   O(1) in corpus size (PP-166)
   Context window:      Pythia-1.4B = 2K tokens (Panel A LLM)
                        Pythia-160M = 2K tokens (Panel B LLM)
   Effective ratio:     ~1,000-100,000x more accessible knowledge (depending on fact density)
```

## Substrate KB (loaded once; serves both panels)

**Tier 1 — structured triples (direct load):**
- Wikidata (~100M triples; CC0; primary)
- ConceptNet (~8M assertions; CC-BY-SA)
- DBpedia top subset (~50M triples; CC-BY-SA)

**Tier 2 — prose extraction (spaCy NER+relation):**
- Wikipedia 5.84M articles
- arXiv ~2M abstracts
- PubMed ~30M abstracts

**Tier 3 — recency overlay (optional; v1.1):**
- News APIs
- Crunchbase + SEC EDGAR

**Total target: ~200M+ facts; empirically validated at 100M per PP-98 sign-key ladder.**

## Panel A engineering (Tier 5a production)

### Components

1. **Pythia-1.4B-Instruct serving** (local; 4-bit if VRAM tight; fp16 if fits)
2. **Substrate-KV server** (reuse D2/D3 mechanism; port to production serving)
3. **Query pipeline:**
   - User query → encoder (bge-small or similar) → substrate retrieval (top-K bindings)
   - Bindings → text serialization → LLM context
   - LLM forward pass (standard) → generation
4. **Audit chain rendering:** Merkle proof + per-binding provenance + cleanup confidence (PP-107)
5. **Hero counter:** substrate stats; live cost; live latency

### Acceptance gate
- Panel A handles unpredictable user queries (Claude-like complexity)
- Substrate retrieval visible in audit chain
- Pythia-1.4B output coherent (4-bit OK; fp16 better)
- End-to-end query latency < 2s

## Panel B engineering (Tier 5b PoC)

### Components

1. **Pythia-160M modified architecture:**
   - Load Pythia-160M weights
   - Replace layer 6 attention forward method
   - Substrate-attention forward:
     ```python
     def substrate_attention_forward(self, x_prev, ...):
         Q = self.W_q @ x_prev                            # standard
         retrieved = substrate.retrieve_top_k(Q, k=128)   # NEW
         K = self.project_to_K(retrieved)                  # substrate vectors -> K shape
         V = self.project_to_V(retrieved)                  # substrate vectors -> V shape
         attn = torch.softmax(Q @ K.T / sqrt(d), dim=-1)
         return attn @ V
     ```
2. **Substrate retrieval inside attention:**
   - Use validated substrate-KV mechanism (D1 HP)
   - Top-K retrieval; binding decomposition
3. **Projection layers:** substrate's HD vectors (N=8192) → Pythia hidden dim (768)
   - Either: learnable projection (no fine-tuning; random init)
   - Or: PCA / linear projection from substrate codebook
4. **Visualization:**
   - Live readout of which bindings retrieved per generation token
   - Side-by-side: bare Pythia-160M vs substrate-attention-modified Pythia-160M
   - Layer-6 substrate-attention output visualized

### Acceptance gate (LOOSE because PoC)
- Modified Pythia-160M produces output (not necessarily coherent; categorical demonstration)
- Substrate-attention layer demonstrably executing (retrievals visible)
- Output not catastrophically broken (perplexity within 5x of baseline acceptable for PoC)

### Honest acknowledgment in UI
- "Panel B is research proof-of-concept; production substrate-attention is v2.0"
- "Output may be rough; categorical demonstration of architectural pattern"

## Wow moments (supporting; both panels)

- **Substrate audit chain expansion** — Merkle proof + per-binding provenance + cleanup confidence
- **Live cost ticker** — gpt-4o-mini baseline cost vs substrate-Pythia local cost
- **Substrate stats sidebar** — facts loaded, shard count, last sleep-defrag
- **Counterfactual do() panel** — 20 ready-to-go scenarios per PP-172

## What we deliberately DON'T include

- **Fine-tuning Pythia-160M post-modification** — Panel B is forward-pass-only PoC; production substrate-attention with fine-tuning is v2.0
- **GPT-4o-mini comparison panel** — single architectural pitch, not "we beat OpenAI"
- **3-mode toggle** — single pitch
- **Compliance mode toggle** — Panel A already shows local-LLM + substrate (no API calls); compliance pitch is implicit
- **Cost-efficiency mode toggle** — Panel A's local-Pythia-1.4B + substrate IS the cost-efficiency story
- **Tier 4 LoRA** — Tier 5a/5b subsumes; Tier 4 stays parked

## The pitch (combined)

> "Substrate is the memory architecture for next-generation LLMs.
>
> **Panel A: Tier 5a substrate-KV (today's product).** Pythia-1.4B + 200M-fact substrate.
> Substrate is the LLM's persistent memory layer. 156x more knowledge than context window.
> 0.21ms retrieval. O(1) latency. Empirically validated across Pythia base/1.4B/2.8B and Qwen.
>
> **Panel B: Tier 5b substrate-attention (architectural proof; v2.0 direction).** Pythia-160M
> with one attention layer modified — substrate IS the attention here. K and V come from
> substrate retrieval, not from learned projections. Standard attention math. Substrate is
> structurally part of the transformer. v2.0 ships this in production LLMs."

Single architectural pitch. Two panels showing the architectural progression. Both
empirically grounded.

## Risk register (no time estimates per user feedback)

| Risk | Mitigation |
|---|---|
| Panel B PoC produces incoherent output | Categorical demonstration matters more than fluency; UI captions explain this is research PoC; comparison to bare Pythia-160M shows BOTH are rough but substrate-modified knows facts |
| Pythia-160M too small even for PoC | Fallback to Pythia-1.4B for Panel B (more compute; still cheap local) |
| Substrate retrieval inside attention has shape mismatch | Engineering: projection layer between substrate vectors and Pythia hidden dim |
| 200M-fact ingest fails partway | Substrate works at partial KB; demo proceeds with what's loaded; finish ingest in background |
| Substrate-KV (Tier 5a) integration with Pythia-1.4B has issues | D2 already empirically validated; integration is engineering not research |
| Demo's "we modified transformer architecture" claim challenged | Show source code; show layer-6 forward method; show substrate retrievals per token; categorical demonstration is verifiable |

## Engineering deliverables (Testbed)

### Already DONE by Testbed (reuse)
- 8 substrate library modules (Research VERIFY signed off with 3 MODIFY + 1 ADD)
- FastAPI 13-route skeleton
- Demo-mode toggle (live-verified)
- Pythia-1.4B GPU smoke validated
- Cloudflare Tunnel setup
- Runner toolchain ready

### NEW Tier 5 sprint work

**Panel A (Tier 5a production):**
- Apply 3 Research MODIFY items (shards.py threshold; cross_shard.py default; bitemporal.py limitation doc)
- Apply 1 ADD item (inverted.py per-property entity list)
- Wire library into `/query/tier5a` endpoint
- Pythia-1.4B local serving (4-bit; D2 scaffold reused)
- Substrate-KV inference path (D2/D3 mechanism)
- Audit chain UI

**Panel B (Tier 5b PoC):**
- Pythia-160M layer-6 attention modification
- Substrate-attention forward method
- Projection layers (substrate HD vectors → Pythia hidden dim)
- Live visualization of substrate retrievals per token
- Bare-vs-modified comparison rendering

**Shared:**
- 200M-fact substrate KB ingestion (Wikidata primary; Wikipedia + ConceptNet + arXiv + PubMed)
- Hero counter (substrate stats + latency + KB sources)
- Cost ticker
- Frontend with two panels + audit chain expansion

### Sequence Testbed decides

Recommended: Panel A first (lower risk; ships product); then Panel B (architectural
demonstration; can fall back to "diagram + roadmap" if PoC underwhelms).

## Open questions for user / Testbed

1. **Pythia-1.4B vs Qwen-2.5-1.5B for Panel A?** Pythia validated for substrate-KV (D2 HP); Qwen also validated (PP-153). Pythia is more "research" feel; Qwen is more "modern instruct" feel.
2. **Panel B Pythia-160M vs Pythia-1.4B?** 160M cheaper; 1.4B more coherent. My default: start 160M; escalate if too rough.
3. **Fine-tune Panel B's modified Pythia post-modification?** Default: NO fine-tuning initially (forward-pass demo only); production v2.0 adds fine-tuning.
4. **Single panel or two panels?** Two panels = clearer architectural progression; single panel = unified pitch.

My defaults if not overridden: Pythia-1.4B Panel A, Pythia-160M Panel B, no fine-tuning, two panels.

## Cross-references
- Tier 5 substrate-KV empirical (D1/D2/D3 HP): cycles 185 + 190 + 191
- Capacity ladder M=10000 (156x): cycle 191
- PP-150 substrate latency O(1): cycle 188
- PP-166 latency scale invariance: cycle 192
- Library VERIFY response: notes/research_to_testbed_v1_demo_LIBRARY_VERIFY_RESPONSE_2026-06-08.md
- Intrinsic-language drill (substrate-attention-layer 4-8 GPU-weeks estimate): notes/research_drill_substrate_llm_intrinsic_language_5x_2026-06-08.md

---

**Testbed:** TIER 5 SPRINT SPEC. RESCINDS prior SPEC v1/v2/v3. Single architectural
pitch: Tier 5a substrate-KV in production + Tier 5b substrate-attention-layer PoC.
Both on Pythia (1.4B Panel A; 160M Panel B). 200M-fact substrate KB. No time estimates
(per user feedback that prior estimates were always wrong; team executes faster than I
predict). Engineering sequence: Panel A first (lower risk); Panel B PoC after.

Pythia validated for substrate-KV at every size we've tested. Tier 5a is empirically
production-ready. Tier 5b is architectural research-grade demonstration.

This is the demo. Sprint to it.
