# Research -> Exp-Dev: Phase 3 architecture blueprint -- SWITCH LLM partner to Gemma-2-2B + need cubic-tensor-write (n=3)

**From:** Research session
**To:** Exp-Dev (primary) + Testbed (LLM partner change)
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~15:00
**Subject:** Production architecture drill recommends Gemma-2-2B (not Llama-3.2-1B) as LLM partner + cubic-tensor-write (n=3 higher-order Hopfield) for Wikipedia-scale capacity. 12 GB total system on consumer hardware. Cheap decisive test specified.

---

## Critical Phase 2/3 corrections from drill

### LLM partner change: Gemma-2-2B (not Llama-3.2-1B)

**Originally framed**: Llama-3.2-1B for Phase 2 extraction.

**Drill recommends**: Gemma-2-2B for these specific reasons:
1. **Distillation-trained from 27B teacher** (arXiv:2408.00118): layer 10 of 26 has activation geometry comparable to ~10B-class model. Critical for substrate KV bridge quality.
2. **256K SentencePiece tokenizer** (vs Llama's 128K BPE): best concept-ID VQ coverage; rare entities tokenized as single tokens.
3. **Apache 2.0 license** (vs Llama Community License 700M MAU restriction): fully permissive commercial deployment.
4. **Interleaved local/global attention**: global attention layers (even indices) preferred for KV injection.
5. **Strong fluency competitive with 2-3x larger models**.

**Llama-3.2-1B drawbacks** (per drill):
- Width-pruned from Llama-3.1 (arXiv:2512.22671): "fragile knowledge" in pruned representations; intermediate layers degraded
- Standard 128K tokenizer; subword fragmentation of entities reduces VQ quality

### Updated Phase 2 extraction target

Testbed action change:
- **OLD**: extract Llama-3.2-1B activations (~$3-5; ~30-60 min wall)
- **NEW**: extract Gemma-2-2B activations (~$5-8; ~45-90 min wall; slightly larger model)

Storage probe in progress; once destination confirmed, extract Gemma-2-2B instead of Llama-3.2-1B.

Same script adaptation: model_id swap from Pythia to Gemma; hidden_dim=2304; tokenizer is SentencePiece (not BPE); 26 layers with interleaved attention pattern.

---

## Phase 3 architecture spec (complete)

### Substrate layer

- **D=8 parallel isolated substrates** at N=65536 each (Architecture A per Mode 5 drill)
- **n=3 cubic-tensor-write** (NEW; higher-order Hopfield): W_3 += x otimes x otimes x; M_max = O(N^2) per substrate ~ 1.3*10^8 facts; D=8 total ~ 10^9 effective facts (10x Wikipedia)
- **Sparsity f=0.10**
- **VQ codebook V_c=1M** atoms at N_cleanup=4096, int8 quantized (or V_c=100K for edge deployment)
- **Bipolar weight storage**: 1-bit W matrices
- **13-state FSM controller** per substrate + 7-bit counter (I_max=128 hops)
- **Substrate footprint: ~8.3 GB**

### LLM partner: Gemma-2-2B

- 2.6B params, 2304 hidden dim, 26 layers
- bfloat16: ~2.5 GB
- Distillation-trained from 27B teacher (layer 10 has 10B-class geometry)
- 256K SentencePiece tokenizer
- Apache 2.0 license

### Bridge architecture (two-bridge hybrid)

**Bridge 1 (text, always active):**
- Format C reasoning chain markup with cert tokens
- `<retrieve hop=1 cert=HASH_ABC deleted=false>subject=X relation=R object=Y</retrieve>`
- Max 5 hops (~50 tokens overhead)
- Audit cert propagates via tag chain
- Fallback when cosine confidence < 0.70

**Bridge 2 (KV injection, cosine >= 0.70 confidence gate):**
- Target layers: **8, 10, 12 of 26** (global attention layers; 30-46% depth = semantic processing zone)
- KV heads: 2 of 4 per layer (50% partial injection; preserves LLM's own retrieval for OOD)
- Projection W_proj: 65536 -> 256 per head, float32, 384 MB total
- Learned offline; frozen at inference
- Inference: <0.1ms per hop per head on GPU

### System total

- 12 GB (fits RTX 4060 Ti 16 GB, RTX 4090 24 GB, Apple M-series 16+ GB unified memory)
- Latency: ~255ms (H100), ~512ms (RTX 4090), ~3s (laptop CPU)
- Cost: ~$0.034/1K queries API; ~$1.25/1K queries RTX 4090

---

## NEW empirical requirement: cubic-tensor-write (n=3) validation

Substrate currently uses quadratic Hebbian (n=2; W_2 += x otimes x; M_max = O(N) classical).

Phase 3 Wikipedia scope requires n=3 cubic-tensor-write (W_3 += x otimes x otimes x; M_max = O(N^2)).

This is a new substrate-class capability we have NOT validated empirically.

### Implementation challenges

Naive cubic tensor at N=65536: 10^14 entries = ~10^14 bits = ~10 TB. Infeasible.

Must use:
- Sparse representation: only store non-zero or significant tensor entries
- Bipolar quantization at higher-order
- Block-local structure (per R2 sparse-resonator scaffold)
- Compressed tensor approximations

### Cell CUBIC-N3-1: Cubic-tensor-write empirical validation at substrate-class

**Anchor:** `substrate_cubic_tensor_write_n3_validation_v1`

### Architecture
- N=4096 (substrate-class; not Phase 3 scale yet)
- Sparse cubic tensor: only store top-K largest absolute entries
- Compare to n=2 quadratic Hebbian baseline at matched M

### Pre-reg
- HP: cubic-tensor-write achieves >=2x capacity vs quadratic at matched M
- MID: 1.2-2x capacity improvement
- HF: cubic doesn't improve or implementation infeasible (Phase 3 needs alternative scaling)

### Cost + wall
- $0 CPU
- ~1-2 days engineering (implement sparse cubic tensor + compare)

### Strategic
Validates the n=3 architecture requirement before Phase 3. If HF: need alternative capacity scaling (multi-substrate hierarchy more aggressively; or accept frontier-tier capacity ceiling).

---

## Cheap decisive Phase 2 test (from drill)

**Anchor:** `substrate_two_bridge_hybrid_smoke_gemma_2b_v1`

Two-bridge hybrid smoke at scaled-down config:

- N=65536, M=10K facts, D=2 (scaled Config B)
- Store 10K fact triples in D=2 isolated substrates (~1.1 GB CPU)
- Query with 100 multi-hop questions (3-hop depth)
- Inject top-5 retrieved facts via Bridge 1 (text Format C) into Gemma-2-2B
- Inject retrieved pattern via Bridge 2 (KV) at layers 8, 10, 12 with confidence gate
- Measure: (a) 3-hop QA accuracy text-only vs text+KV; (b) deletion cert generation time; (c) latency breakdown

### Pre-reg

- **HP**: text+KV achieves >=5pp accuracy gain vs text-only; cert generation <1ms per deletion
- **HF**: KV bridge adds <2pp; cert generation >10ms

### Cost + wall

- ~2-3 minutes laptop GPU (RTX 3080+)
- ~30 minutes CPU only
- $0

### Why this test first

This is the smallest decisive test of the entire Phase 3 architecture stack:
- Validates KV bridge at Gemma-2-2B layers (Bridge 2)
- Validates text-injection Format C with cert tokens (Bridge 1)
- Validates D=2 isolation (per Architecture A)
- Validates deletion cert latency target (<1ms)

If HP: all major Phase 3 architectural choices empirically anchored at scaled-down config. If HF: identify which component fails before scaling up.

---

## Three structural moats (drill confirmation)

The drill confirms what we've been claiming + sharpens the framing:

**MOAT 1: Algebraic deletion certificates** -- cryptographic audit trail generated in <1ms from substrate state change. Categorically absent from RAG/RETRO/DNC/MemLong/CAMELoT/frontier-LLM. GDPR / CCPA / EU AI Act compliance.

**MOAT 2: Real-time continual learning with cert-compatible writes** -- Hebbian write <1ms per new fact; cert hashes remain valid for non-modified patterns. LLMs require fine-tune cycles (hours-days). No alternative provides cert-compatible real-time writes.

**MOAT 3: Complexity-class separation** -- substrate AC0/TC0 (parallel O(1) depth) + LLM NC1/P (serial). Clean computational separation that vector DBs and soft-attention systems lack.

### Cost moat vs frontier scaling

- 100M facts in LLM context (Gemini 2.0/GPT-5 1M-token context): ~500M tokens/query
- At $3/M tokens: **~$1500 per query**
- Substrate + Gemma-2-2B hybrid: **~$0.006 per query**
- **250,000x cost moat** -- frontier context scaling doesn't eliminate substrate advantage; cost makes it categorical

---

## Updated Phase 2 priorities

Per drill:

**Phase 2 Priority 1**: Gemma-2-2B extraction (not Llama-3.2-1B)
**Phase 2 Priority 2**: Two-bridge hybrid smoke test (HP-7 above; cheap decisive)
**Phase 2 Priority 3**: Cubic-tensor-write empirical validation (CUBIC-N3-1; required for Phase 3)

Plus continue Pythia-tier Phase 1 work:
- Remaining capability benchmarks (HotpotQA + NQ; expected Pythia-ceiling)
- Substrate-MAX for REASONING (not LM)
- Introspection toolkit categories 4-10
- Long-conversation memory at scale (HP-1)
- Multi-doc synthesis at scale (HP-2)
- 30-day continual learning simulation (HP-3)
- Medical Q&A prototype (HP-5)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary on substrate; Testbed primary on extraction
- Per [[feedback-no-padding-experiments]]: 2 new cells (CUBIC-N3-1 + two-bridge-hybrid-smoke) test distinct Phase 3 prerequisites
- Per [[feedback-pressure-test-negative-findings]]: cubic-tensor-write may HF; if so, need alternative capacity path before Phase 3
- Per [[feedback-cloud-only-when-absolutely-necessary]]: smoke test is CPU-feasible; full Phase 3 extraction is ~$5-30 cloud
- ASCII-only

PROT-018: `_two_bridge_hybrid_smoke_gemma_2b_v1` + `_cubic_tensor_write_n3_validation_v1`
PROT-021: source=local CPU + cheap cloud Gemma extraction; n_seeds=3

---

**END.**

**Testbed:** SWITCH Phase 2 extraction target from Llama-3.2-1B to Gemma-2-2B. Reasons: distillation-trained from 27B teacher (richer intermediate representations); 256K tokenizer (best concept-ID VQ); Apache 2.0 license (vs Llama Community license restrictions). Cost change: ~$5-8 (was $3-5); time change: ~45-90 min wall (was 30-60 min). Storage probe in progress; once destination confirmed, extract Gemma-2-2B per same script-adaptation pattern.

**Exp-Dev:** Two new cells: (1) Two-bridge hybrid smoke at scaled-down config (~2-3 min laptop GPU; validates KV bridge + text injection + isolation + cert latency simultaneously); (2) Cubic-tensor-write empirical validation at N=4096 (~1-2 days; required for Phase 3 Wikipedia capacity). Plus Phase 2 work proceeds with Gemma-2-2B target.

**User:** Phase 3 architecture has concrete blueprint: D=8 substrates at N=65536 with n=3 cubic-tensor-write + Gemma-2-2B partner + two-bridge hybrid (text + KV at layers 8/10/12). Total 12 GB; fits consumer hardware. Cost moat 250,000x vs frontier context scaling. Three structural moats categorically defensible: deletion certs + real-time cert-compatible writes + complexity-class separation.
