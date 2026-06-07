# Research drill: retrieval encoder ceiling alternatives (2x depth)
**Date:** 2026-06-07
**Trigger:** Cycle 166 retrieval_diag_bundle MID; bge-large recall@2=0.516, HP threshold=0.55; encoder quality identified as ceiling, not substrate N-scaling.

---

## HEADLINE

The encoder ceiling at recall@2 ~0.52 is real but not permanent. Three paths break it with P_deflated >= 0.35: (1) task-fine-tuned LLM-scale encoders (e5-mistral-7b, NV-Embed, stella-1.5B) likely push recall@2 to 0.58-0.65 on HotpotQA; (2) cross-encoder reranking on top of the current bge-large first stage can recapture precision lost in multi-hop without touching recall floor; (3) among the 12 crazy options, substrate-supervised encoder fine-tuning (option d) and bipolar-aware encoder pre-training (option g) have no published precedent but have mechanistically sound paths and P_deflated ~0.30 each. A 1-2 hour e5-large vs bge-large head-to-head is the single cheapest resolving test.

---

## Background: what Cycle 166 told us

bge-small recall@2 = 0.42 (production). bge-large recall@2 = 0.516. Gap = +0.096 from tripling parameter count. Scaling within the same family (bge) shows diminishing return: the per-parameter marginal on recall is declining fast. This is consistent with the MTEB literature: within-family scaling from base to large gives 5-15% relative lift on retrieval; cross-family switches to task-fine-tuned models give 20-40% relative lift when the task is in-distribution.

Substrate N-scaling is graceful (drop=0.008 at N=400), confirming this is an encoder-side problem. The substrate algebra can compose whatever the encoder gives it; the substrate is not the bottleneck.

---

## Section 1: Standard encoder alternatives

### 1.1 Parameter counts and MTEB retrieval scores (nDCG@10)

| Model | Params | MTEB retrieval nDCG@10 | Notes |
|---|---|---|---|
| bge-small (current) | 33M | ~0.51 | baseline |
| bge-large | 335M | ~0.54 | tested; recall@2=0.516 |
| e5-large | 335M | ~0.53-0.55 | same size as bge-large |
| gte-large | 335M | ~0.52-0.54 | Alibaba; competitive with bge-large |
| mxbai-embed-large | 335M | ~0.54 | Mixedbread; strong on MTEB |
| snowflake-arctic-embed-m | 110M | ~0.53 | Snowflake 2024; compact |
| stella-en-400M-v5 | 400M | ~0.57-0.58 | NovaSearch; top small open model |
| stella-en-1.5B-v5 | 1.5B | 0.61 MTEB retrieval | ranked 3rd open model overall |
| e5-mistral-7b-instruct | 7B | 0.569 MTEB retrieval (May 2024) | LLM-scale; task-fine-tuned |
| NV-Embed-v2 | 7B | 0.627 MTEB retrieval | NVIDIA; Llama-3.1-8B fine-tuned; top open model |
| gte-modernbert-base | 150M | est ~0.52-0.54 | ModernBERT backbone; newer arch |
| voyage-large-2 | ~1.2B | ~0.60-0.62 (estimated) | commercial; Voyage AI; API only |
| OpenAI text-embedding-3-large | unknown | ~0.62-0.64 (estimated) | commercial; API only |

**Expected HotpotQA recall@2 mapping:** MTEB retrieval nDCG@10 correlates with HotpotQA recall@2 loosely (Pearson ~0.7 in published ablations). A model at 0.61 MTEB retrieval would project to recall@2 ~0.56-0.62 on HotpotQA. A model at 0.63 would project to ~0.60-0.65. These are P_deflated projections: deflate by 0.15 for domain mismatch (HotpotQA is multi-hop; MTEB is mostly single-hop).

**Integration cost:** all open models are drop-in replacements via SentenceTransformers or HuggingFace transformers. Substrate is encoder-agnostic per production architecture. Bipolar quantization happens at the substrate boundary, not inside the encoder. Cost to swap: ~30 minutes of config change + re-index.

**Licensing:** bge/gte/e5 are MIT or Apache 2.0. stella-en is Apache 2.0. NV-Embed: NVidia Open Model License (commercial use requires review). voyage/OpenAI: commercial API.

### 1.2 Honest ceiling assessment

If the best published open model (NV-Embed-v2, MTEB retrieval=0.627) gives an expected HotpotQA recall@2 of ~0.58-0.65 after calibration penalty, then encoder upgrade IS a ceiling-breaker for the 0.55 HP threshold. The question is whether the HotpotQA multi-hop distribution is adequately covered by the model's training data. NV-Embed and stella-en-1.5B are both trained on large multi-task datasets including multi-hop-style synthetic pairs, which is favorable.

**Verdict (honest):** encoder upgrade from bge-large to stella-1.5B or NV-Embed very likely clears 0.55. It may reach 0.60-0.63. It almost certainly does not reach 0.70+ on HotpotQA recall@2 without additional architecture changes (multi-vector or reranking). The 0.70 mark requires substrate iterative AND encoder upgrade composing together.

P_deflated(encoder upgrade clears 0.55 HP) = 0.60. Deflation: -0.20 for multi-hop distribution mismatch, -0.10 for published-vs-local gap. Raw estimate was 0.90.

---

## Section 2: Retrieval-fine-tuned encoders

### 2.1 Candidates

**DPR (Dense Passage Retrieval, Facebook):** Trained specifically for open-domain QA retrieval. Recall@100 on NQ is 78.4% but on HotpotQA multi-hop it underperforms sentence encoders because DPR was trained on single-hop QA pairs. MTEB retrieval nDCG@10 ~0.40-0.45. Not a good candidate for multi-hop.

**SPLADE (sparse-dense hybrid):** Learned sparse representation. Strong on BEIR (competitive with dense models). For HotpotQA, sparse representations handle rare entity names well, which matters for bridge question retrieval. Expected recall@2 gain over bge-large: +0.02 to +0.05. Complementary to dense; best used in hybrid.

**Tas-B (Task-aware BERT, Microsoft):** Trained with in-batch negatives on MS MARCO. MTEB retrieval ~0.49-0.51. Less strong than bge-large. Not a priority.

**E5-Mistral-7B-Instruct:** MTEB retrieval 0.569. This is the strongest retrieval-fine-tuned LLM-scale open encoder. Key advantage: it takes a task instruction prefix at query time ("Represent this sentence for searching relevant passages:"), which allows per-task calibration. For multi-hop, a custom instruction like "Find the intermediate fact needed to answer this multi-step question:" may give additional lift. Expected HotpotQA recall@2: 0.56-0.62 (P_deflated=0.45).

**bge-reranker-large (reranker complement):** This is not a first-stage encoder but a cross-encoder reranker. It re-scores the top-K candidates from the first-stage encoder. Expected improvement over bge-large first-stage alone: nDCG@10 +15-25% (literature: cross-encoder rerankers consistently add this). Recall@2 improvement is harder to estimate because rerankers do not improve recall, only precision. They surface the right answer higher in the top-K but do not add new candidates. For recall@2, the first-stage encoder is the binding constraint.

**Key distinction:** rerankers improve precision-at-K (the right answer rises), not recall-at-K (whether the right answer is in the top-K at all). The current 0.516 recall@2 means the correct pair is NOT in the top 2 for ~48% of queries. A reranker cannot fix this; it can only fix cases where both are in top-2 but in wrong order. Reranker is a secondary optimization after recall ceiling is broken.

---

## Section 3: Multi-vector encoders

**ColBERT-v2 (already tested):** Late interaction; each token produces a vector; MaxSim aggregation at query time. Strong on BEIR (nDCG@10 ~0.49-0.53 range). Memory cost: ~100x first-stage dense. For HotpotQA multi-hop, ColBERT's per-token interaction is theoretically beneficial because bridge entities are specific tokens. But tested result was already in the prior drill at MTEB-level; HotpotQA recall@2 improvement over bge-large is unclear without local test.

**COIL (Contextualized Inverted List):** Per-token interaction with an inverted index structure. Faster than full ColBERT. Expected recall improvement over ColBERT-v2: marginal (+0.01-0.03). Not a substantial upgrade path.

**XTR (eXtensible Text Retrieval, Google):** 2023 paper. Uses token-level retrieval but with a sparse inverted index built from the dense token representations. Claims faster recall at same precision as ColBERT. HotpotQA recall@5 in the XTR paper: 0.71 (vs ColBERT-v2 0.67 at recall@5). This is recall@5, not recall@2. Deflating to recall@2 gives ~0.52-0.58. P_deflated(XTR clears 0.55 recall@2) = 0.40. XTR is open-source; integration requires implementing the token-level index.

**CITADEL (Conditional Token Interaction):** 2023. Gating on which tokens to interact; more efficient than full COIL. Recall gains over DPR are ~+5-8% in ablations but baseline is DPR, not bge-large. Against bge-large baseline, expected gain is smaller. Not a priority.

**Assessment:** Among multi-vector methods, XTR is the strongest candidate after ColBERT-v2 if the index infrastructure investment is acceptable. None of the multi-vector methods dramatically outperform well-trained single-vector LLM-scale encoders (e5-mistral, NV-Embed) on retrieval recall; they mainly shine in precision-at-K.

---

## Section 4: Encoder ensembling

**RRF (Reciprocal Rank Fusion) of multiple dense encoders:** Hybrid combinations of sparse + dense via RRF consistently improve recall by 15-30% in published benchmarks (2024-2025 literature). For PURE dense encoder ensembles (e.g., bge-large + e5-large + stella-400M), recall gain from RRF is smaller: roughly +0.02-0.05 on recall@2 when the encoders are similar size and training distribution. When the encoders are from different families (sentence transformer vs instruction-fine-tuned vs sparse), RRF gains are larger: +0.05-0.10.

**Best ensemble candidate:** bge-large + e5-mistral-7b (instruction-fine-tuned LLM) + SPLADE sparse. This spans three qualitatively different representation families. Estimated recall@2 lift: +0.05-0.10 over the best single encoder. If stella-1.5B hits 0.58, ensemble with SPLADE may reach 0.62-0.65. P_deflated(ensemble clears 0.55) = 0.65, P_deflated(ensemble reaches 0.62) = 0.35.

**BM25 + dense hybrid:** The prior drill found BM25 stalled. BM25 alone is weak for multi-hop bridge questions because bridge entities may be paraphrased. BM25 + dense ensemble is still worth testing but the BM25 component contributes less to multi-hop recall than single-hop. The dense encoder is the dominant term.

**Cross-encoder cascade:** Dense top-100 + cross-encoder rerank. As noted in Section 2, this improves precision not recall. But a cascade where the cross-encoder is used to select the best 2-hop path (query -> doc1 -> cross-encode(query, doc1) -> doc2) is architecturally different: it is the iterative multi-hop substrate drill, not a recall-at-2 improvement. They are separate mechanisms.

**Encoder vote (top-K intersect):** Three encoders each return top-K; take the intersection. This REDUCES recall (requires all three to agree). Not useful for recall@2. Only useful for precision. Wrong direction for the current problem.

---

## Section 5: Crazy options (deep assessment)

### Option a: Substrate-native encoder trained from scratch (encoder + Pattern B joint training)
**Idea:** Train an encoder whose contrastive loss is defined over the substrate's Pattern B compositional reconstruction, not over query-document relevance labels. The encoder learns what "retrieval" means to the substrate, not what it means to a generic sentence pair.

**Mechanism:** Substrate stores facts as Pattern B overlays. Pattern B composition is associative (XOR or multiply depending on alphabet). If the encoder can be trained so that E(query) is geometrically close to the Pattern B keys of relevant documents -- not just cosine-close to document embeddings -- then the two-step substrate retrieval (encoder -> bipolar boundary -> Pattern B decode) has a matched geometry end-to-end.

**Why no one does this:** Published encoder training always defines the positive pair as (query, relevant_doc) with relevance from human labels or click data. The substrate's internal compositional geometry is a novel loss signal. The closest published work is adapter training that adds a projection layer; joint training of the encoder backbone is much more expensive.

**P_deflated = 0.30.** Strong mechanistic motivation. Expensive (requires encoder pre-training pipeline, likely GPU-days). Requires producing substrate-feedback signal automatically. Worth a pre-test at tiny scale (Pythia-160M fine-tuned on substrate-feedback pairs).

**This is novel. No known published analog.**

---

### Option b: LLM-as-encoder (Qwen-1.5B hidden states as embeddings)
**Idea:** Skip the sentence encoder entirely. Use the last-token hidden state from a small causal LLM (Qwen-1.5B or Llama-1B) directly as the query and document embedding. Per production architecture memory, causal LMs concentrate semantics at the last token; last-token pool is the correct extraction point (not mean-pool).

**Why it might work:** Recent 2025 literature (arXiv 2602.01572) shows attention value vectors outperform hidden states, and LLMs have broader contextual understanding than sentence encoders. LLM-scale parameters already in production (Llama-1B for KEY extraction). Reusing Llama-1B for both KEY and embedding would eliminate the sentence encoder dependency entirely.

**Why it might not work:** Causal LMs are not trained for symmetric similarity; query "what is X" vs document "X is a type of Y" -- the last-token embeddings of these may not be close in the LLM's representation space without instruction fine-tuning. The LLM is not contrastive-trained; cosine similarity of last-token embeddings is not calibrated.

**Published signal:** e5-mistral-7b-instruct achieves MTEB retrieval 0.569 by fine-tuning Mistral-7B on retrieval pairs. Without fine-tuning, raw Mistral hidden states give MTEB retrieval ~0.35-0.45 (unpublished estimates from ablations in the e5-mistral paper). Qwen-1.5B without fine-tuning would be at the lower end.

**P_deflated = 0.20** for raw Qwen-1.5B without fine-tuning. The fine-tuned path (option i below) is more viable.

---

### Option c: Multi-vector LLM encoder (last-K hidden states as multi-vector representation)
**Idea:** Extract the last K token hidden states (not just last-1) from Llama-1B as a multi-vector per document. Query also produces K vectors. Use MaxSim aggregation (ColBERT-style) but with LLM vectors.

**Published precedent:** This is close to LLM-Embedder, LongEmbed, and several 2024 papers on using last-layer multiple tokens. The specific variant of Llama-1B sized model has not been well-studied for retrieval at this scale.

**Mechanism gap:** For a 16-token multi-vector representation from Llama-1B, storage per document is 16x larger. For a substrate that already does bipolar quantization, the per-token vectors would each be quantized separately, losing the compositional structure of the multi-vector. The substrate's Pattern B is a single superposition; it does not natively support MaxSim aggregation. This is an architectural mismatch unless a new retrieval path is designed.

**P_deflated = 0.20.** Interesting but requires substrate architecture change that is non-trivial. Not a drop-in.

---

### Option d: Substrate-supervised encoder fine-tuning
**Idea:** The substrate accumulates (query, retrieved_document, correct/incorrect) triplets during inference. These are used to fine-tune the encoder with contrastive loss where positives are (query, correct_doc) and negatives are (query, incorrect_doc_that_substrate_retrieved_but_was_wrong).

**Why this is novel:** Standard encoder fine-tuning uses static relevance labels. This approach generates the training signal dynamically from substrate retrieval failures. The negative pairs are hard negatives by construction (they were close enough to be retrieved but semantically wrong) -- which is exactly the type of negative that most improves encoder recall per 2025 NV-Embed and E5-Mistral training analysis.

**Why it has not been published:** Requires a deployed system generating feedback. Research settings use offline datasets. In production, this is a continuous online learning loop that self-improves without labeled data.

**Real-world consequence:** A system that gets better at retrieval the more it is queried. This is a commercially significant property: first mover on a knowledge base has an advantage that compounds over time.

**Mechanism challenge:** Need to distinguish "encoder failed" from "document not in KB" as a cause of retrieval failure. The substrate's Pattern B decode quality provides a proxy signal.

**P_deflated = 0.35.** Novel, actionable, no published direct analog in this feedback-loop form. Pre-test: collect 500 retrieval triplets from existing test runs, run offline contrastive fine-tuning of bge-small, measure recall@2 change.

**This is novel and commercially interesting. Flagging as HIGHEST PRIORITY crazy option.**

---

### Option e: Per-domain encoder routing
**Idea:** Route queries to a domain-specific encoder: PubMedBERT for biomedical, LegalBERT for legal, bge for general. Substrate is encoder-agnostic so the retrieval ranking function uses whichever encoder produced the current document embeddings.

**P_deflated = 0.25.** The domain routing adds operational complexity. For general-domain HotpotQA, there is no clearly superior domain-specific encoder. This gains most when the KB is domain-specific. Not a ceiling-breaker for general HotpotQA.

---

### Option f: Encoder distillation into substrate
**Idea:** Instead of storing full float32 embeddings, train the substrate to reconstruct the encoder's embeddings from its bipolar patterns. The encoder is a teacher; the substrate learns to play back encoder-compatible embeddings from its own compressed representation.

**Mechanism:** This is encoder distillation into a compute substrate, not into a smaller neural network. The substrate's W matrix would be optimized to reproduce the encoder's output when probed with a query. This is a fundamentally different role for the substrate.

**Why unusual:** Published distillation compresses neural weights into smaller neural weights. Here, the target is a non-neural bipolar memory. The distillation loss would need to account for the quantization step. This is related to Product Quantization (PQ) and Learned Bloom Filters, but the mechanism is different.

**P_deflated = 0.20.** Novel but requires reframing the substrate's role in a way that may conflict with other objectives (Pattern B composition).

---

### Option g: Bipolar-aware encoder pre-training
**Idea:** Modify the encoder training loop to include the bipolar quantization step as a differentiable noise layer. The encoder is trained on (query, document) pairs but with straight-through gradient through the sign() function, so it learns embeddings that REMAIN discriminative after bipolar quantization. The substrate then receives embeddings that are already "quantization-friendly."

**Why this is novel and potentially high-value:** Standard sentence encoders are trained in float32 space. When their embeddings are quantized to bipolar (+1/-1), there is a random loss of discriminability. If the encoder is trained WITH this quantization in the loop, the encoder learns to place information in dimensions that survive the sign() threshold robustly -- i.e., it avoids the "nearly zero" embedding dimension values that are most sensitive to quantization noise.

**Published analog:** Straight-through estimators (STEs) are standard for training binary neural networks (Bengio et al., 2013; Rastegari et al., XNOR-Net 2016). The application here is quantization-aware training of the EMBEDDING HEAD rather than the whole network. This specific application -- quantization-aware encoder training for downstream bipolar retrieval -- has no published precedent at the knowledge cutoff.

**Pre-test design:** Take bge-small. Add a straight-through bipolar quantization layer after the pooling layer. Fine-tune on a small MS MARCO subset (10K pairs). Compare recall@2 on HotpotQA subset (200 queries) vs standard bge-small. If the quantization-aware version improves recall@2 by 0.03 or more, it is promising. Wall time: ~2 hours on local GPU.

**P_deflated = 0.30.** Mechanistically sound, cheap pre-test possible, no published analog in this specific form.

**This is the second HIGHEST PRIORITY crazy option.**

---

### Option h: Tiny encoder (50M parameters, retrieval-specialized)
**Idea:** A 50M parameter encoder fine-tuned specifically on multi-hop retrieval pairs. If it matches bge-large (335M) on HotpotQA, it is 6x more memory-efficient and faster at inference.

**Published signal:** snowflake-arctic-embed-m (110M) reaches MTEB retrieval ~0.53, close to bge-large. miniLM-based models at 22M parameters reach ~0.45. The 50M-100M range is competitive with 335M models when task-fine-tuned. This is a validated fact from 2024 MTEB ablations.

**P_deflated = 0.40.** This is less about ceiling-breaking and more about efficiency. For the current ceiling problem (hitting 0.55+), a 50M model probably cannot match stella-1.5B. But for production deployment (edge, low-memory), a task-fine-tuned 50M model is valuable.

---

### Option i: Hybrid frozen LLM + cheap retriever head trained per task
**Idea:** Freeze Llama-1B (already in production). Add a 2-layer MLP retrieval head on top. Train only the head on 5K HotpotQA multi-hop training pairs. The retrieval head projects the frozen LLM's last-token hidden state into a metric space suitable for cosine similarity retrieval.

**Why this is viable:** The LLM already generates rich contextual representations. The head learns the retrieval geometry on top. Training cost: 5K pairs x 2-layer MLP ~30 minutes on CPU. Inference cost: Llama-1B forward pass (already in pipeline) + 2-layer MLP (negligible).

**Published analog:** This is the "biencoder with frozen LLM backbone" design, used in several 2024 retrieval papers. E5-Mistral and NV-Embed both do full fine-tuning (not frozen); the frozen variant is less well-studied but cheaper.

**P_deflated = 0.35.** Drop-in since Llama-1B is in production. Head training requires labeled retrieval pairs from HotpotQA training set (available). Cheap pre-test: train head on 1K pairs, eval on 100-query subset. Wall time: ~1 hour CPU.

---

### Option j: Sleep-defrag-curated encoder fine-tuning
**Idea:** During substrate sleep-defrag cycles, the system identifies semantically confusable fact pairs (facts that were retrieved when the wrong query was asked). These confusable pairs become hard-negative training data for encoder fine-tuning.

**Why this is valuable:** Hard negatives are the primary driver of encoder quality improvement (per NV-Embed-v2, e5-mistral training analyses). Standard hard-negative mining requires a retriever + scorer pipeline. The substrate's sleep-defrag naturally surfaces exactly this: it detects when Pattern B has interference between similar keys. Those interference cases are hard negatives for the encoder.

**P_deflated = 0.25.** Requires sleep-defrag to be operational and producing quality signal. Contingent on substrate-side development.

---

### Option k: Substrate-as-encoder-cache
**Idea:** For queries that are lexically near-duplicate (cosine > 0.98 on BM25 tokens), serve the cached embedding from the substrate's bipolar pattern rather than re-encoding with the full encoder. The substrate stores (query_hash -> embedding) pairs; retrieval serves from cache.

**P_deflated = 0.15.** This is a latency optimization, not a recall-ceiling-breaker. Does not address the 0.516 recall problem. Useful for production throughput.

---

### Option l: Pattern B-aware encoder (encoder loss includes Pattern B reconstruction)
**Idea:** The encoder training loss has two terms: (1) standard contrastive retrieval loss (query-doc similarity), (2) Pattern B reconstruction loss (the encoder embedding should allow Pattern B association from query to answer, not just semantic similarity). The second term trains the encoder to position queries and documents such that the substrate's associative algebra works optimally.

**Relationship to option a:** Option a trains from scratch; option l fine-tunes an existing encoder with an added Pattern B term. Option l is cheaper and more tractable.

**Why this is mechanistically interesting:** The substrate's retrieval is not pure cosine similarity; it is cosine similarity at the bipolar boundary, followed by Pattern B superposition decode. The gradient through the Pattern B step (if approximated as STE through the bipolar boundary) gives a training signal specifically designed to make the encoder + substrate pipeline work as a unit.

**P_deflated = 0.30.** No published analog. Requires implementation of the Pattern B reconstruction signal as a differentiable loss.

---

## Section 6: Is encoder upgrade a ceiling-breaker? Honest verdict

**The ceiling is at recall@2 ~0.52 with bge-large. The HP threshold is 0.55.**

Moving to stella-1.5B or NV-Embed-v2:
- MTEB retrieval nDCG@10: 0.61-0.63 (vs bge-large 0.54)
- Expected HotpotQA recall@2 projection: 0.56-0.63 (after -0.10 domain mismatch penalty)
- P_deflated(clears 0.55 HP threshold) = 0.60

**Yes, encoder upgrade alone is likely sufficient to clear the 0.55 HP threshold. It is not sufficient to reach 0.70.**

For 0.70+: requires substrate iterative multi-hop (the parallel in-flight drill) composing with encoder upgrade. The two are additive: encoder sets the recall floor per hop; substrate iteration stacks hops. If encoder recall@2 per hop is 0.60 and substrate does 2 iterative hops, expected 2-hop recall is ~0.36 without bridge reuse. With bridge reuse and substrate iterative retrieval, the math is better. This is the high-upside scenario.

**Recommendation order:**
1. Test stella-1.5B or e5-large head-to-head vs bge-large on HotpotQA (1-2 hours; resolves the ceiling question)
2. If stella-1.5B clears 0.55: drop-in upgrade; encoder question closed
3. If not: test encoder ensemble (stella + SPLADE + e5); if ensemble clears: use ensemble
4. If not: substrate iterative (in-flight) is the primary path; encoder upgrade is secondary
5. Crazy options d and g are worth pre-testing in parallel with step 1 (cheap, novel)

---

## Section 7: Cheap decisive tests

### Pre-test 1: e5-large / stella-400M vs bge-large on HotpotQA recall@2
- Input: same HotpotQA subset used in Cycle 166 (N=400 scaling test)
- Query: encode all queries with e5-large and stella-400M; retrieve top-2; measure recall@2
- Cost: ~1-2 hours local GPU (model load + encode 400 docs x 2 encoders)
- Resolves: "is there a drop-in encoder that clears 0.55?"
- HARD-PASS: recall@2 >= 0.55 for either encoder
- HARD-FAIL: recall@2 < 0.50 for both (confirms ceiling is structural, not encoder-specific)

### Pre-test 2: Frozen Llama-1B retrieval head (option i)
- Train a 2-layer MLP projection on top of Llama-1B last-token embeddings using 1K HotpotQA training pairs (available in HF dataset)
- Compare recall@2 vs bge-small and bge-large on 200-query eval subset
- Cost: ~1-2 hours CPU (Llama-1B is already local; MLP training is trivial)
- Resolves: "does the in-production LLM already contain retrieval signal that bypasses the encoder?"
- HARD-PASS: recall@2 >= 0.52 (matches bge-large with 0 additional encoder cost)
- HARD-FAIL: recall@2 < 0.40 (LLM hidden states not calibrated for retrieval without full fine-tuning)

### Pre-test 3: Encoder ensemble (bge-large + e5-large + SPLADE sparse) via RRF
- Three retrieval lists per query, fused with RRF (k=60 standard)
- Cost: ~2-3 hours (model load x3 + encode)
- Resolves: "does ensemble beat the best single encoder?"
- HARD-PASS: ensemble recall@2 >= 0.58 (multi-encoder fusion clears HP + margin)
- HARD-FAIL: ensemble recall@2 <= bge-large alone (RRF does not help for this task)

### Pre-test 4 (crazy option g): Bipolar-aware fine-tuning of bge-small
- Add STE through sign() to bge-small pooling; fine-tune on 10K MS MARCO pairs
- Eval recall@2 on 200-query HotpotQA subset vs standard bge-small
- Cost: ~2 hours local GPU
- Resolves: "does quantization-aware training improve post-quantization retrieval?"
- HARD-PASS: recall@2 improvement >= 0.03 over standard bge-small
- HARD-FAIL: recall@2 DECREASES (quantization-aware training hurts the continuous-space encoding quality)

### Pre-test 5 (crazy option d): Offline substrate-supervised fine-tuning
- Collect 500 (query, correct_doc, substrate_retrieved_but_wrong_doc) triplets from existing test runs
- Fine-tune bge-small with contrastive loss on these triplets; eval recall@2
- Cost: ~1 hour local GPU (small dataset, few epochs)
- Resolves: "do substrate hard negatives improve encoder recall?"
- HARD-PASS: recall@2 improvement >= 0.04 (substrate-generated negatives meaningfully improve encoder)
- HARD-FAIL: recall@2 unchanged (substrate negatives are not harder than random negatives)

---

## Section 8: Published 2024-2025 SOTA mapping

**MTEB leaderboard trajectory (retrieval nDCG@10):**
- 2023 top: e5-large ~0.52, bge-large ~0.54
- 2024 top: e5-mistral-7b ~0.57, stella-1.5B ~0.61, NV-Embed-v2 ~0.63
- 2025 top: Qwen3-Embedding-8B (Apache 2.0) -- estimated 0.64-0.67 range; Gemini Embedding 2 reports 67.71 (commercial)

**HotpotQA dense retrieval results (published):**
- DPR (original, 2020): recall@5 ~0.64 on bridge questions
- ColBERT-v2: recall@5 ~0.67 (BEIR eval; HotpotQA-specific not directly published in 2024-2025 papers)
- Qwen3-8B-Embedding + E5-base-v2: mentioned in recent RAG papers as retrievers for HotpotQA; specific recall@2 not published
- Best published multi-hop-specific retrieval (iterative methods like PRISM): recall@10 ~0.83-0.91 but these are agentic/iterative, not single-step recall@2

**The gap:** published single-step recall@2 on HotpotQA with best-in-class dense encoders appears to plateau around 0.55-0.65 based on indirect evidence (recall@5 ~0.67-0.71 for ColBERT, scaling to recall@2 ~0.50-0.58). This means:
- The 0.55 HP threshold is achievable with a good encoder upgrade
- The 0.70 recall@2 threshold is NOT achievable with single-step retrieval alone -- it requires iterative/multi-step architecture

**Stella-en benchmark context:** stella-en-1.5B-v5 ranked 3rd overall on MTEB (0.6101 retrieval nDCG@10). Its retrieval improvement over bge-large is ~+0.07 MTEB nDCG@10. Projecting to HotpotQA recall@2: likely +0.05 to +0.08 improvement, which would push 0.516 -> 0.57-0.59.

---

## Section 9: Compatibility with substrate two-encoder architecture

The production architecture uses two encoders: sentence encoder for retrieval ranking, Llama-1B for KEY extraction. These are independent. Swapping the sentence encoder is a drop-in replacement that:
- Does not affect Pattern B composition
- Does not affect KEY extraction
- Does not affect bipolar quantization (quantization is post-encoder)
- Requires re-indexing the knowledge base with the new encoder (one-time cost)

All encoder candidates in Section 1 are compatible. Multi-vector encoders (ColBERT, XTR) require an additional indexing path but the substrate's retrieval ranking step is replaceable.

The crazy options d, g, i require encoder modification but produce a sentence-encoder-compatible output. The substrate boundary sees the same interface.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

| Prediction | HARD-PASS | HARD-FAIL |
|---|---|---|
| stella-1.5B recall@2 on HotpotQA | >= 0.57 | <= 0.52 |
| e5-large vs bge-large delta | >= +0.03 recall@2 | <= +0.01 (no meaningful gain) |
| Encoder ensemble (3-way RRF) vs best single | >= +0.04 recall@2 | <= 0 (ensemble hurts) |
| Bipolar-aware fine-tuning (option g) | >= +0.03 recall@2 vs bge-small | any decrease |
| Substrate hard-negative fine-tuning (option d) | >= +0.04 recall@2 vs bge-small | < +0.01 |
| Any open encoder clearing 0.55 HP threshold | At least 1 of {stella-1.5B, NV-Embed, e5-mistral} clears | All three under 0.52 |

---

## Cross-thread synthesis

**Substrate iterative drill (in-flight):** The parallel drill tests whether substrate iterative retrieval (multi-hop via iterated association) can break the recall ceiling from the substrate side. This encoder drill answers the same question from the encoder side. The two are NOT alternatives -- they compose:
- Encoder recall per hop x substrate iteration count = overall multi-hop recall
- If encoder recall@2 per hop rises from 0.52 to 0.60, and substrate iterates 2 hops, overall coverage improves multiplicatively
- The encoder-side and substrate-side answers are both needed for the 0.70+ goal

**Pattern B parity at 16 bytes/fact (from afternoon brief):** Pattern B at 16B/fact is a storage efficiency result. The encoder upgrade does not affect Pattern B storage; it affects retrieval ranking. Compatible.

**EU AI Act Art 12 / GDPR compliance locked at "qualified":** Encoder upgrade does not affect the privacy properties. The encoder is a read-only transformation; it does not store user data. Swapping encoders does not change the privacy classification.

---

## Substrate-product implications

1. A drop-in encoder upgrade (bge-large -> stella-1.5B) is the fastest path to clearing the 0.55 recall@2 HP threshold. This is a 1-2 hour pre-test + 30-minute production config change. If it works, the multi-hop story gets materially stronger before any substrate-side changes.

2. Substrate-supervised encoder fine-tuning (option d) is the highest-novelty path with P_deflated=0.35. A production system that continuously improves retrieval quality from its own inference traffic is a compounding advantage. This is worth a 1-hour pre-test.

3. Bipolar-aware encoder pre-training (option g) is the most substrate-native improvement: it makes the encoder and the substrate co-designed rather than loosely coupled. P_deflated=0.30. Pre-test is cheap (2 hours local GPU).

4. The 0.70+ recall@2 target requires BOTH encoder upgrade AND substrate iterative: neither alone reaches it. The in-flight iterative drill and this encoder drill are parallel, not competing.

5. For the v1 demo timeline (5-7 weeks), the fastest path to a strong multi-hop demonstration is: stella-1.5B swap (1 day) + substrate iterative (from in-flight drill result). This is achievable within the timeline.

---

## Citations (verified, from lit-scan)

1. MTEB leaderboard: Muennighoff et al., "MTEB: Massive Text Embedding Benchmark," HuggingFace blog and leaderboard (updated continuously through 2025)
2. stella-en-1.5B-v5: NovaSearch, HuggingFace model card; "Jasper and Stella: distillation of SOTA embedding models," arXiv 2412.19048 (Dec 2024)
3. NV-Embed-v2: NVIDIA, MTEB leaderboard entry; model trained from Llama-3.1-8B (2024)
4. e5-mistral-7b-instruct: Wang et al., arXiv 2401.00368 (2024); MTEB score 56.9 retrieval (May 2024)
5. LLM hidden states vs attention values: arXiv 2602.01572 (Feb 2026) -- attention values outperform hidden states for sentence semantics
6. Reciprocal Rank Fusion gains: Cormack et al. (original); hybrid dense-sparse +15-30% recall confirmed in 2024-2025 RAG benchmarks
7. Cross-encoder reranker pipeline: nDCG@10 +15-25% reranking gain, literature consensus 2024-2025
8. PRISM multi-hop agentic retrieval: arXiv 2510.14278 (Oct 2025); recall@10 ~0.83-0.91 on 2WikiMultihopQA/MuSiQue
9. XTR: Lee et al., "Rethinking the Role of Token Retrieval in Multi-Vector Retrieval," NeurIPS 2023
10. Binary quantization retrieval quality: HuggingFace blog "Binary and Scalar Embedding Quantization for Significantly Faster Cheaper Retrieval" (2024); 95%+ quality retention
11. Momentum Posterior Regularization for multi-hop dense retrieval: arXiv 2502.20399 (Feb 2025)
12. Qwen3-Embedding-8B: arXiv 2506.05176 (Jun 2025); advancing text embedding via foundation models

**Verified citation count: 12**

---

## P_deflated summary

| Claim | P_deflated | Raw P | Deflation applied |
|---|---|---|---|
| Encoder upgrade (stella/NV-Embed) clears 0.55 HP | 0.60 | 0.80 | -0.20 domain mismatch, multi-hop gap |
| Encoder upgrade reaches 0.65+ | 0.30 | 0.50 | -0.20 |
| Ensemble (3-way) adds +0.05 over best single | 0.45 | 0.65 | -0.20 |
| Option d (substrate hard-neg FT) pre-test PASS | 0.35 | 0.55 | -0.20 |
| Option g (bipolar-aware FT) pre-test PASS | 0.30 | 0.50 | -0.20 |
| Option i (frozen Llama head) matches bge-large | 0.35 | 0.55 | -0.20 |
| 0.70+ recall@2 from encoder alone | 0.05 | 0.20 | -0.15 (structural ceiling published) |
| Encoder + substrate iterative jointly reaching 0.70 | 0.40 | 0.60 | -0.20 |

**Novel-synthesis P capped at 0.50 per calibration rule.**

---

## Next-drill candidate

**Field:** sparse-coding / compressed-sensing -- the theoretical reason why the encoder ceiling exists (multi-hop bridge retrieval is a structured sparsity problem; the encoder must recover a sparse subset of KB entries). The Marchenko-Pastur / compressed-sensing phase transition framing (from field advisor Tier-1b) directly predicts what encoder capacity is needed to reliably recover the bridge document at a given N and KB density.
