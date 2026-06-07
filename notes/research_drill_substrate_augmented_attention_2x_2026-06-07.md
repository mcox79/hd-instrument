# Research Drill: Substrate-Augmented Attention in LLM Generation (2x)
## Date: 2026-06-07
## Discipline: Theoretical / attention augmentation / lit-scan / no empirical

---

## HEADLINE

Cross-attention from frozen LLM hidden states to externally retrieved facts is a proven, trainable paradigm (RETRO, LongMem, M+). The substrate can serve as that external store with per-chunk or per-generation query cadence. Per-token cadence is too expensive unless sparse-triggered (FLARE pattern). Multi-hop benefit is real but modest: +0.05-0.10 F1 on HotpotQA relative to one-shot RAG, based on iterative retrieval literature; deflated P_deflated = 0.35 for this particular substrate-to-attention bridge because no direct substrate-as-KV-attention precedent exists in published work. The frozen LLM + new cross-attention adapter path is the lowest-risk entry; 2-3 weeks engineering.

---

## 1. Architecture Specification

### 1.1 Core Mechanism

Standard causal self-attention at layer L computes:

  Attn(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V

where Q, K, V are all derived from the context window.

The proposed extension adds a second attention term:

  Attn_aug(Q, K_sub, V_sub) = softmax(Q * K_sub^T / sqrt(d_k)) * V_sub

where K_sub and V_sub are derived from substrate-retrieved facts, and Q is the same LLM hidden state query used in standard attention. The final output at that layer is a gated sum:

  h_out = alpha * Attn_context + (1 - alpha) * Attn_sub + h_residual

alpha is a learned scalar (or per-head) gate, initialized near 1.0 so the frozen LLM path dominates at the start of training.

### 1.2 Substrate Query Generation

At layer L, take the hidden state h_L of the current token (or the last token of the current chunk). Apply a small linear projection:

  q_sub = W_q_sub * h_L    (dim: d_k_sub, e.g. 256)

Submit q_sub to the substrate retriever. The substrate returns top-K fact embeddings {f_1, ..., f_K}.

Project fact embeddings to K and V:

  K_sub = W_k_sub * F    (K x d_k)
  V_sub = W_v_sub * F    (K x d_v)

Only W_q_sub, W_k_sub, W_v_sub, alpha are trained. LLM weights frozen.

### 1.3 Query Cadence Options

Three cadences, with tradeoffs:

| Cadence | Retrieval calls | Added latency | Best for |
|---|---|---|---|
| Per-generation (once at start) | 1 | ~10 ms | Factual completion, low-hop |
| Per-chunk (every 64 tokens) | N_chunks | 10 ms * N_chunks | Medium-hop, RETRO-style |
| Per-layer | N_layers | 240 ms for 24-layer | NOT recommended baseline |
| Adaptive / sparse trigger | 0 to N_tokens | ~10-50 ms total | Multi-hop, FLARE-style |

Per-layer is the worst latency case. For a 24-layer model at 10 ms/retrieval: 240 ms overhead per forward pass. At 100 tokens that is the entire generation budget. Do not default to per-layer.

Per-chunk (RETRO-style) is the published precedent. RETRO incurs ~35% pretraining compute overhead, but that is pretraining-time; inference-time overhead is proportional to retrieval calls per chunk, not per-layer (RETRO attaches CCA at every other transformer layer, but retrieval itself is once per chunk of 64 tokens).

Adaptive trigger (FLARE pattern) is the best multi-hop cadence: trigger a retrieval when token generation confidence falls below a threshold, or when a named entity or relation token is emitted. This keeps median retrieval calls at 1-3 per generation even for multi-hop questions.

---

## 2. Multi-Hop Benefit Analysis

### 2.1 Where Standard RAG Fails on Multi-Hop

Standard retrieve-then-generate: query is issued once before generation begins. For a two-hop question (A -> bridge B -> answer C), the initial query can retrieve A's facts but not B's, because B is unknown at query time. The generation must first produce B (or a latent representation of B) before B-relevant facts become retrievable.

This is the "bridge-ID at the retrieve-then-generate boundary" limitation. The LLM has to either (a) already know B from parameters, or (b) reason bridge B from A's retrieved facts without B's own retrieved facts, which produces hallucination when B is rare or recent.

### 2.2 How Cross-Attention-During-Generation Addresses This

With adaptive substrate query triggered at layer L when h_L encodes a bridge-candidate entity:

- Token 0..N: LLM generates up to the bridge token using context + initial retrieval
- Bridge token emitted (or hidden state crosses confidence threshold)
- New substrate query issued with h_L as query vector
- Substrate returns B-facts as K_sub, V_sub
- Subsequent tokens attend to B-facts directly

This is structurally equivalent to iterative retrieval (FLARE, IRCoT, EfficientRAG) but executed inside the forward pass rather than as an outer loop. The key difference: the query vector is a continuous hidden state (not a discrete string), which means the substrate query captures semantic intent before B is fully decoded to text.

### 2.3 Quantitative Estimate

Iterative RAG methods (FLARE, EfficientRAG, BridgeRAG) report +0.04-0.12 F1 on HotpotQA over single-shot RAG. Cross-attention-during-generation should deliver a similar range, with the upper bound contingent on (a) substrate recall quality and (b) quality of the bridge-trigger signal.

Deflated P_deflated estimate: 0.35 that substrate-specific cross-attention beats one-shot RAG by >= +0.05 F1. Rationale for deflation: the theoretical mechanism is sound and has iterative-RAG analog precedent, but the substrate-as-KV-attention bridge is novel and the continuous-query-vector advantage over string-query is unverified.

Hard-fail threshold: if substrate cross-attention does NOT beat standard one-shot RAG by at least +0.03 F1 on HotpotQA at Pythia-160M scale, the architecture adds cost without net retrieval benefit and the mechanism is not worth scaling.

---

## 3. Implementation Options

### Option A: Cross-Attention Adapter (Primary Recommendation)

Architecture: frozen LLM + new cross-attention sublayer inserted after each of layers {L/4, L/2, 3L/4, L} (4 attachment points for 24-layer model).

Trainable parameters: W_q_sub, W_k_sub, W_v_sub, alpha gate per attachment point. Approximately 4 * 4 * d_model * d_k = ~4M params for d_model=1024, d_k=256.

Training: supervised on HotpotQA or multi-hop QA with frozen backbone. The cross-attention heads learn to use substrate facts; LLM weights unchanged.

Latency: per-chunk (every 64 tokens) retrieval. 1-3 substrate calls per generation. Adds 10-30 ms.

Engineering cost: 2-3 weeks. Need: substrate query projection layer, K/V projection of retrieved facts, gated attention combiner, training loop. Reference code: RETRO chunked cross-attention, LongMem SideNet.

Precedent quality: HIGH. RETRO (Borgeaud et al. 2022), LongMem (Wang et al. 2023), M+/SuMem all demonstrate this pattern works on frozen LLM variants.

### Option B: LoRA on Attention Heads

Architecture: LoRA low-rank updates on Q/K/V projection matrices in attention layers. LoRA delta matrices learn to route queries toward substrate-retrieved content.

Difference from Option A: does not add a new cross-attention sublayer. Instead, LoRA updates teach existing attention heads to partially act as retrieval heads. This requires feeding substrate facts into the context window (as prefix) rather than as separate K/V.

Trainable parameters: rank-8 LoRA on Q/K projections across all layers. ~2M params.

Known limitation: LoRA on attention heads hurts retrieval quality per empirical findings (cap_map entry: LoRA hurts retrieval). This is a known negative result in the substrate context. LoRA changes the effective key space, which degrades cosine similarity lookups.

Verdict: lower priority than Option A. Try only if Option A training is unstable.

Engineering cost: 1-2 weeks.

### Option C: Sparse Attention (Adaptive Trigger, FLARE-Style)

Architecture: same as Option A (cross-attention adapter) but retrieval is triggered only when a confidence signal crosses a threshold.

Confidence signal options:
- Entropy of token distribution at layer L > threshold (high uncertainty -> retrieve)
- Named entity / relation token detected in last N tokens (bridge signal)
- LLM hidden state diverges from its running mean by > k sigma

This is the highest-value extension because it eliminates wasted retrieval on tokens where context suffices. Median retrieval calls drop to 1-3 per generation vs. per-chunk cadence.

Engineering cost: 3 weeks (Option A + confidence signal + trigger logic).

Lit precedent: FLARE (Jiang et al. 2023) demonstrates exactly this with token-level confidence triggering; their improvement is +0.06-0.08 F1 on multi-hop vs. single-shot RAG.

P_deflated for adaptive trigger beating per-chunk: 0.45. The mechanism is directly analogous to FLARE; the only novel part is using hidden-state entropy rather than softmax token probability.

### Option D: Multi-Substrate Cross-Attention (Crazy Option c)

Architecture: separate cross-attention heads for base substrate and customer-specific substrate. The LLM attends to both independently and the outputs are combined:

  h_out = alpha_base * Attn(Q, K_base, V_base) + alpha_cust * Attn(Q, K_cust, V_cust) + Attn_context

This directly addresses the product requirement of per-customer knowledge bases. The base substrate holds general facts; the customer substrate holds domain-specific facts.

Theoretical grounding: multi-head attention is already a sum of independent attention heads. Extending to two external KV sources is a direct generalization. No published precedent at this exact topology, but the math is identical.

Tradeoff: doubles substrate retrieval calls. 20-60 ms per generation. The latency is acceptable if retrieval is async / batched.

Engineering cost: 3-4 weeks.

P_deflated that multi-substrate beats single-substrate on domain-specific QA: 0.42. Reasonable but unverified.

### Option E: Substrate Gradient Through Attention (Crazy Option e)

Architecture: do NOT freeze substrate. Allow the cross-attention training gradient (from W_q_sub, W_k_sub, W_v_sub) to flow back into the substrate binding matrix W via dL/dW_sub.

This is substrate-learning-from-LLM-attention-signal. The substrate would update its stored fact representations to be better aligned with the LLM's query distribution.

Risk: gradient through the retrieval step requires differentiable retrieval (e.g., soft nearest-neighbor, Gumbel-softmax over fact index). Standard top-K retrieval is not differentiable.

Workarounds: REALM (Guu et al. 2020) demonstrated differentiable retrieval via MIPS inner product with straight-through estimator. Dense Passage Retrieval (DPR) updates are a related precedent.

Engineering cost: 4-6 weeks. Much higher complexity.

P_deflated that this improves over fixed substrate: 0.28. High implementation risk; differentiable retrieval through the substrate binding matrix is non-trivial.

### Option F: Substrate as Bridge-Conditioned Decoder Layer (Crazy Option d)

Architecture: after the LLM produces a bridge-entity token, route the hidden state to a substrate "decoder module" that generates the next N tokens from accumulated substrate bindings rather than from LLM parameters.

This is a hybrid generation: LLM generates most tokens; substrate decoder generates tokens over a specific fact span.

Precedent: BridgeRAG (2025) uses bridge-conditioned retrieval. The substrate-decoder variant is a further specialization where substrate output is projected directly to vocabulary logits.

Risk: two output distributions (LLM logits + substrate logits) need a mixing mechanism. Entropy-gated mixing is the natural choice.

Engineering cost: 4-5 weeks.

P_deflated: 0.25. Novel and high-risk but directly addresses the "bridge-ID boundary" problem with a different structural solution than cross-attention.

---

## 4. Latency Analysis

Reference latency numbers (theoretical; no empirical measurement done in this drill):

| Operation | Estimated time | Basis |
|---|---|---|
| Single substrate retrieval (top-K=8) | 5-15 ms | Approximate FAISS/ANN inner product at N=65k |
| Per-generation cadence | 10 ms total | One query at start |
| Per-chunk (64 tok) cadence | 10-30 ms | 1-3 chunks per 200-token generation |
| Per-layer cadence (24 layers) | 120-360 ms | 12-24 retrieval calls if every other layer |
| Adaptive / sparse trigger | 10-40 ms | 1-4 triggers per generation at median |
| LLM forward pass (Pythia-160M) | ~50 ms | CPU; GPU ~5 ms |
| LLM forward pass (Llama-1B) | ~80 ms CPU, ~8 ms GPU | Reference estimate |

Key constraint: per-token retrieval at 10 ms/token and 100 tokens/generation = 1 second retrieval overhead. This is prohibitive even for interactive use. Per-token cadence is only viable if retrieval is batched, async, and the GPU forward pass is the bottleneck (not retrieval). For the substrate at N=65k on CPU, assume retrieval at ~10 ms; GPU speeds this up but does not eliminate the per-token problem.

Per-chunk cadence (RETRO pattern) is the practical baseline. 35% overhead at pretraining time per RETRO's published benchmark. Inference-time overhead is proportional only to retrieval calls, not model size.

---

## 5. Cheap Pre-Tests (3 Options)

### Pre-test 1 (Cheapest): Pythia-160M + cross-attention probe on HotpotQA

Setup: Pythia-160M with 2 frozen layers. Add one cross-attention sublayer after layer 4 (of 6). Train W_q_sub, W_k_sub, W_v_sub on HotpotQA training set. Substrate is a simple FAISS index of HotpotQA supporting facts (no substrate binding; this pre-test uses a standard dense retriever to isolate cross-attention mechanism from substrate-specific representation).

Metric: F1 on HotpotQA dev set.

Comparison: same Pythia-160M with one-shot RAG (retrieve-then-prepend to context).

HARD-PASS: cross-attention >= +0.05 F1 over one-shot RAG.
MID-BAND: cross-attention within +0.01 to +0.04 F1 of one-shot RAG (mechanism works but marginal gain).
HARD-FAIL: cross-attention at or below one-shot RAG F1 (cross-attention adds no value; do not proceed to Option C or D).

Wall time: 2-4 hours on local GPU. Cost: $0 local.

This pre-test is explicitly designed to isolate the cross-attention mechanism, NOT to validate substrate-specific representations. Passing this test authorizes Option A engineering.

### Pre-test 2: Adaptive trigger threshold sweep on Pre-test 1 model

Setup: use the trained cross-attention model from Pre-test 1. Sweep token entropy threshold from 0.3 to 0.9. Count average retrieval calls per generation and F1.

Metric: F1 vs. retrieval calls per generation curve (Pareto front).

HARD-PASS: a threshold exists where F1 >= Pre-test 1 HARD-PASS value AND retrieval calls <= 2 per generation on average.
HARD-FAIL: every threshold either degrades F1 or keeps retrieval calls at per-chunk levels (no Pareto gain from adaptive trigger).

Wall time: 1 hour on top of Pre-test 1.

### Pre-test 3: Multi-substrate attention prototype (Option D validation)

Setup: split HotpotQA supporting facts into "base" (Wikipedia facts) and "domain" (sports or science subset). Train two cross-attention heads on the Pre-test 1 model. Evaluate on domain-specific questions.

Metric: F1 on domain subset vs. single-substrate cross-attention.

HARD-PASS: multi-substrate >= +0.03 F1 over single-substrate on domain questions.
HARD-FAIL: no improvement or regression on domain questions.

Wall time: 3-5 hours.

---

## 6. Engineering Sequencing

### v1.5 (Next 2-3 weeks, authorized if Pre-test 1 passes)

Deliverable: Option A cross-attention adapter on Pythia-160M (or Llama-1B BASE) attached to substrate retriever at 2 attachment points (layers L/2 and L).

Scope:
- W_q_sub / W_k_sub / W_v_sub projection layers
- Gated attention combiner (alpha gate)
- Substrate query interface (HyperVec -> FAISS -> top-K -> project to K/V)
- Training loop on HotpotQA

Does NOT include: adaptive trigger, multi-substrate, gradient through substrate.

Gate to v2.0: Pre-test 1 must show >= +0.03 F1 on HotpotQA (below hard-pass but above hard-fail) at Pythia-160M scale before Llama-1B cross-attention is authorized.

### v2.0 (Weeks 4-7, conditional on v1.5 gate)

Deliverable: Option C (adaptive trigger) + Option D (multi-substrate) on Llama-1B BASE.

Prerequisites: v1.5 gate passed + pre-test 2 Pareto validation passed.

Engineering delta from v1.5: confidence signal module, trigger logic, second substrate head (Option D adds ~1 week).

Does NOT include: Option E (differentiable substrate gradient) in v2.0. Too high implementation risk for the product timeline.

---

## 7. Falsifiable Predictions

### HARD-PASS Conditions (authorize next engineering phase)

HP-1: Pythia-160M cross-attention adapter achieves F1 >= 0.42 on HotpotQA dev (vs. ~0.37 expected for same model with one-shot RAG at this scale). Deflated from theoretical ceiling of 0.55.

HP-2: per-chunk retrieval adds <= 40 ms latency on local GPU (Pythia-160M, 200-token generation, 3 substrate calls).

HP-3: adaptive trigger (Pre-test 2) achieves HP-1 F1 with <= 2.5 average retrieval calls per generation.

### HARD-FAIL Conditions (halt this architectural direction)

HF-1: cross-attention F1 <= one-shot RAG F1 + 0.02 (cross-attention adds noise, not signal; mechanism is broken).

HF-2: latency overhead > 200 ms per generation at per-chunk cadence on GPU (makes interactive use infeasible at current substrate speed).

HF-3: multi-hop F1 improvement disappears when bridge entity is NOT in top-5 substrate retrieval results (meaning substrate recall, not cross-attention architecture, is the binding constraint; architectural change won't help).

---

## 8. Cross-Thread Synthesis

### Connection to Tier 4 (Arch 8 + 5)

Current Tier 4 baseline: substrate as attached memory; LLM consumes text output of substrate retrieval. The present proposal is a structural upgrade from text-mediated to attention-mediated coupling. The text-mediated path (Tier 4 baseline) is the right starting point because it requires no LLM modification. The cross-attention path is the Tier 4 -> Tier 4.5 upgrade when text-mediated performance plateaus on multi-hop tasks.

### Connection to Tier 5 (Arch 8 substrate as KV-cache)

Tier 5 replaces the LLM KV cache with substrate vectors. The present proposal does NOT replace KV cache; it adds a second attention pathway. These are complementary, not competing. Tier 5 requires LLM modification at the KV-cache level; the present proposal only requires a new cross-attention sublayer. The present proposal is lower risk and lower coupling.

### Connection to Whitening + PCA (production architecture)

The substrate query vector q_sub = W_q_sub * h_L is a learned projection of LLM hidden states onto the substrate's PCA-whitened representation space. This is a direct bridge between LLM representation geometry (anisotropic, layer-dependent) and substrate representation geometry (whitened, uniform variance). The W_q_sub matrix is the learned alignment transform. This is a non-trivial alignment problem; expect training to require >500 steps to stabilize the query projection.

### Connection to LoRA-hurts-retrieval finding

Option B (LoRA on attention heads) is predicted to fail because LoRA updates change the effective cosine similarity geometry of the attention keys, which is exactly the mechanism through which the substrate's whitened representations are indexed. This is consistent with the cap_map finding that LoRA hurts retrieval. Use Option A (new cross-attention sublayer, frozen LLM) to avoid this conflict.

### Connection to FLARE / BridgeRAG

FLARE (Jiang et al. 2023) demonstrated that token-level confidence-triggered retrieval outperforms single-shot RAG by +0.06-0.08 F1 on multi-hop tasks. BridgeRAG (2025) demonstrated bridge-conditioned retrieval with structured SVO query generation. The present proposal combines the FLARE trigger mechanism with substrate-native query vectors (continuous hidden states) rather than string queries, which is the novel contribution. Whether continuous queries outperform string queries is the key unknown; P_deflated = 0.40 that continuous queries are better on substrate-specific fact representations.

---

## 9. Substrate-Product Implications

The cross-attention adapter is the most natural LLM integration path that does not require modifying the LLM or retraining it. This is a product strength: customers keep their existing LLM (frozen) and add the substrate as an attention-level knowledge layer. The engineering deliverable is a lightweight adapter module (~4M params) that can be trained on customer-specific QA pairs in hours.

The multi-substrate option (Option D) directly enables the product scenario where each customer has a separate knowledge substrate that is independently maintained and updated. The base substrate holds shared general knowledge; customer substrates hold proprietary domain knowledge. The LLM attends to both simultaneously with learned mixing weights.

The latency profile (10-30 ms per generation at per-chunk cadence) is compatible with interactive use on GPU inference. The bottleneck is substrate retrieval speed, not LLM inference. At N=65k substrate vectors on GPU, retrieval time should be under 5 ms, making the total overhead < 15 ms per generation.

The key engineering risk is query-space alignment: the LLM hidden states at layer L are not in the same representation space as the substrate's whitened vectors. The W_q_sub projection must learn this alignment. If the alignment is poor, substrate facts will not be retrieved by the right hidden states. This is mitigated by the v1.5 pre-test, which validates alignment at Pythia-160M scale before committing to full engineering.

---

## 10. Calibration Summary

| Claim | Raw P | Deflation | P_deflated | Notes |
|---|---|---|---|---|
| Cross-attention adapter beats one-shot RAG on multi-hop | 0.55 | -0.20 | 0.35 | Novel substrate-attention bridge; no direct precedent |
| FLARE-style adaptive trigger improves Pareto curve | 0.65 | -0.20 | 0.45 | FLARE precedent is strong; substrate-native query is novel |
| Multi-substrate (Option D) beats single-substrate on domain QA | 0.60 | -0.18 | 0.42 | Structurally sound; unverified at this substrate topology |
| Option B (LoRA) fails on retrieval quality | 0.80 | 0.00 | 0.80 | Cap_map empirical result already; deflation does not apply |
| Option E (gradient through substrate) works without differentiable retrieval | 0.10 | 0.00 | 0.10 | Not viable without REALM-style differentiable MIPS |
| Per-layer retrieval (24 layers) is impractical | 0.90 | 0.00 | 0.90 | Simple latency arithmetic; not a novel claim |

All novel-synthesis P estimates capped at 0.50 per calibration discipline.

---

## 11. Citations (Verified via lit-scan)

1. Borgeaud et al. (2022). Improving language models by retrieving from trillions of tokens. (RETRO). arXiv:2112.04426. Cited for: chunked cross-attention mechanism, 35% pretraining overhead, per-chunk retrieval cadence.

2. Wang et al. (2023). LongMem: Enhancing long-term memory in large language models. Cited for: frozen LLM backbone + trainable SideNet for KV-pair retrieval and fusion.

3. Liu et al. (2024). MemLong: Retrieval Causal Attention for frozen LLMs. Cited for: per-layer cross-attention retrieval architecture.

4. Jiang et al. (2023). FLARE: Active Retrieval Augmented Generation. Cited for: token-level confidence-triggered retrieval, +0.06-0.08 F1 on multi-hop vs. single-shot RAG.

5. Guu et al. (2020). REALM: Retrieval-Augmented Language Model Pre-Training. Cited for: differentiable retrieval via MIPS inner product, relevant to Option E.

6. BridgeRAG (2025). Training-Free Bridge-Conditioned Retrieval for Multi-Hop QA. arXiv:2604.03384. Cited for: bridge entity identification, structured query generation for two-hop retrieval.

7. Trained Persistent Memory for Frozen Decoder-Only LLMs (2026). arXiv:2603.22329. Cited for: six memory injection methods on frozen GPT-2; cross-attention + Hebbian + slot-based achieved 7-18% retained-memory scores.

8. Memory-Augmented Transformers: A Systematic Review (2025). arXiv:2508.10824. Cited for: taxonomy of memory integration mechanisms (attention fusion, gated control, associative retrieval).

9. EfficientRAG (2024). Cited for: iterative refinement of queries for multi-step reasoning, latency considerations.

10. M+/SuMem (2024). Cited for: per-layer cross-attention to retrieved distant-past tokens, co-trained per-layer retrievers.

Verified citation count: 10 (all found via lit-scan; abstracts confirmed via search results).

---

## Next-Drill Candidate

Field: free-probability (F4 Free cumulants / Voiculescu kappa_n). Field advisor ranks this first by yield-cost-adjacency score (5.5). Not related to this drill; recommended as next orthogonal scan.

Within this drill's thread, the most productive follow-up is Pre-test 1 execution (Pythia-160M cross-attention on HotpotQA). This converts the 0.35 P_deflated estimate to empirical data within 2-4 hours.
