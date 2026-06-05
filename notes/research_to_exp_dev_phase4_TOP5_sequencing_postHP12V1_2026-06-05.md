# Research -> Exp-Dev: Phase 4 TOP 5 sequencing (post-HP-12 V1 demo) + 2 drills in flight

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~18:30
**Subject:** User confirmed TOP 5 PURSUE-NOW priorities + Phase 4 sequencing + encoder bottleneck drill. Plus dev-speed acceleration drill dispatched (new dimension). TOP 5 cells route to Exp-Dev with explicit "after HP-12 V1 demo" timing to preserve focus.

---

## Strategic frame (user-confirmed)

HP-12 V1 demo is THE priority for next 2-3 days. After it ships (screen-recordable demo of certified per-fact deletion + real-time write moats on a 1B+substrate system), Phase 4 starts.

Phase 4 work expands the substrate-LLM hybrid into the validated commercial thesis: 1B-scale LLM + substrate ~ 10-30B standalone on structured tasks. Combined with the existing cert / real-time-write / TC0 / cost moats, this is the categorically-defensible product.

---

## Phase 4 TOP 5 sequencing (post-HP-12 V1)

### Phase 4a: shared infrastructure (~5-8 days)

**Cell PHASE4-INFRA-1: Encoder bottleneck infrastructure**
- Currently in research drill (2x; dispatched ~18:00; ETA ~30 min)
- Drill output: optimal encoder architecture (off-the-shelf sentence-BERT vs distilled 50M from Llama-1B vs custom VQ-aware)
- Plus VQ codebook design (V_c=100k-1M; sparsity; bipolar quantization)
- Plus latency targets per use case (hallucination detection <1ms; working memory loop <50ms)
- Engineering follow-on: ~5-8 days after drill lands

**Cell PHASE4-INFRA-2: Bridge B (KV injection) production infrastructure**
- Currently exists in scaffolds; needs production-grade implementation
- Inject at Gemma-2-2B layers 8/10/12 (per Phase 3 blueprint)
- Confidence gate cosine >= 0.70
- 2 of 4 KV heads per layer
- W_proj 65536 -> 256 per head (384 MB total; learned offline; frozen at inference)
- Engineering: ~3-5 days

These two pieces (encoder + Bridge B) are the SHARED INFRASTRUCTURE for the rest of Phase 4. Build once.

---

### Phase 4b: commercial thesis validation (~8-12 days)

**Cell PHASE4-IDEA2-1: Working Memory Loop (Idea 2 from 20-ideas drill)**
- 1-3B LLM + substrate iterative query loop
- LLM emits sub-query (~50 tokens) -> VQ encode -> substrate retrieval -> accumulator update (Rule 8 + beta*) -> KV inject state -> next iteration
- Halt when cosine(state_i, state_{i-1}) < 0.05 OR K_max=12 reached
- HARD-PASS: HotpotQA 2-hop EM >= 0.45 with 1B+substrate at K_max=7 (vs ~0.25-0.35 baseline)
- Comparison to ReAct/AutoGPT/Self-RAG: substrate ~3.5x faster in LLM compute (0.3 vs 7 passes per iter)
- Engineering: 8-12 days

**Cell PHASE4-IDEA17-1: Continual Learning via KV Injection (Idea 17)**
- LLM frozen
- Substrate ingests new knowledge in real-time (Hebbian writes <1ms each)
- During inference, substrate teaches LLM via Bridge B KV injection at confidence gate
- Effectively makes LLM mutable WITHOUT fine-tune cycles
- Shares Bridge B infrastructure with Phase 4b above
- Engineering: 8-12 days (parallel with IDEA2-1 if Bridge B ready)

Both validate the "1B + substrate ~ 10-30B" commercial thesis.

---

### Phase 4c: layered features (~10-15 days)

**Cell PHASE4-IDEA3-1: Hallucination Detection (Idea 3)**
- Every LLM output span -> fast encoder (22M sentence-BERT) -> VQ concept-ID -> substrate lookup
- If cos < threshold AND domain coverage > 0.80: mark "UNSUPPORTED"
- Variants: hard reject (verified KBs) / soft warning / citation requirement / alternative-fact suggestion
- HARD-PASS: F1 >= 0.57 on HaluEval high-coverage domain at <10ms/span CPU
- Engineering: 10-15 days

**Cell PHASE4-IDEA8-1: Chain-of-Thought Cache with Cert (Idea 8)**
- Multi-hop reasoning steps stored in substrate
- Future similar queries retrieve cached reasoning traces
- Meta-learning: substrate gets faster over time
- Each cached trace has cert provenance (which input -> which reasoning -> which output)
- Compounds cert moat at near-zero marginal infrastructure
- Engineering: 5-8 days

Both compound the audit/cert moat at low marginal cost.

---

### Phase 4d: categorical capability demo (~5-8 days)

**Cell PHASE4-IDEA1-1: K-hop Native Reasoning (Idea 1)**
- VSA algebra performs reasoning hops without LLM forward passes
- Chain: h0 = encode(q) -> r1 = cleanup(W^T * h0) -> h1 = h0 XOR hop_key_1 XOR r1 -> r2 = cleanup(W^T * h1) -> ...
- Each hop is O(N) bipolar ops; cleanup error 2-5%/hop at N=4096; K_max ~8
- HARD-PASS: K=3 accuracy >= 0.70 at N=4096, V_c=1024
- Speedup: 100x-20,000x vs LLM-mediated reasoning (revised from "1000x" claim)
- Engineering: 5-8 days (cheap; validates cleanup-error envelope governing 6 other ideas)

---

## Total Phase 4 (4a + 4b + 4c + 4d): ~30-45 days from HP-12 V1 demo

If parallelism on infrastructure pays off: could be 20-30 days.

---

## Cost estimates

| Phase | Engineering | Cloud |
|---|---|---|
| Phase 4a (infrastructure) | 8-13 days | $10-30 |
| Phase 4b (commercial thesis) | 8-12 days | $30-80 |
| Phase 4c (layered features) | 15-23 days | $50-100 |
| Phase 4d (categorical demo) | 5-8 days | $20 |
| **Total Phase 4** | **36-56 days** | **$110-230** |

Way under cloud budget. Engineering time is the constraint.

---

## Timing: AFTER HP-12 V1 demo lands (~2-3 days)

Do NOT start Phase 4 cells while HP-12 V1 is in build. Focus is THE priority for this week.

Phase 4 cells route now for awareness + design review, but execution starts after HP-12 V1 demo screen recording is shipped.

---

## Drills in flight (Phase 4a informers)

**Drill 1: Encoder bottleneck design (Phase 4a infrastructure)**
- Dispatched ~18:00; ETA ~30 min
- Output: optimal encoder + VQ codebook + latency targets

**Drill 2: Dev-speed acceleration (new dimension)**
- Dispatched ~18:00; ETA ~40 min
- 16 ideas across training/tools/process/wild
- Output: recommended dev-speed investment portfolio (1-3 picks; total ~10-20 eng-days)
- Could 3-5x research throughput; would compound Phase 4 timeline

Both drill outputs will inform Phase 4a sequencing precisely.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: each cell tests distinct architectural hypothesis
- Per [[feedback-substrate-value-framing-2026-05-26]]: product-engineering work weighted higher than additional theoretical confirmation; TOP 5 are all product-engineering
- Per user 2026-06-05 ~18:00: explore all 20 ideas eventually; Phase 4 sequencing locked
- ASCII-only

---

**END.**

**Exp-Dev:** Phase 4 TOP 5 sequenced + cost-estimated. Total ~30-45 days post-HP-12-V1; ~$110-230 cloud. Execution STARTS AFTER HP-12 V1 demo lands (~2-3 days). Cells route now for design review awareness only.

**Testbed:** No new asks beyond gmpy2 install + optional Llama weights (already routed). FAISS HNSW env fix still standing for V2.

**User:** TOP 5 routed with explicit "after HP-12 V1" timing. Phase 4 totals ~30-45 days + ~$110-230 cloud. Plus 2 drills in flight (encoder bottleneck + dev-speed acceleration); both privacy-locked; both inform Phase 4a infrastructure choices.
