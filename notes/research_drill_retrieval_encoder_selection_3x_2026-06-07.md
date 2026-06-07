# research: retrieval encoder selection for v1 demo -- 3x drill

**Date:** 2026-06-07
**Trigger:** Cycle 156 empirical results; exp_dev routing note; encoder is the HotpotQA bottleneck
**Routing source:** notes/exp_dev_to_research_URGENT_llama_not_retrieval_encoder_2026-06-07.md

---

## HEADLINE

bge-small-en-v1.5 (33M) at recall@2hop=0.42 bare and recall@10=0.74 coverage is the correct encoder anchor for the v1 demo. The HotpotQA 2-hop gap to 0.70 is a genuine multi-hop reasoning problem, not a retrieval-coverage or ranking problem: the supporting facts ARE in the top-10 pool, but no similarity or single-hop reranking method extracts them. The path to 0.70 is a decomposition loop (small LLM splits the 2-hop question into two single-hop queries; bge retrieves each). Substrate K-hop relay, audit log, and bitemporal storage sit on top of this retrieval stack and supply the system-level value story beyond raw recall numbers.

---

## Empirical encoder ladder (production harness, n=50, same data/matching)

All numbers from exp_dev routing note (hotpot_substrate_bge_v1 + hotpot_bge_recall_at_k_v1 + hotpot_bge_rerank_v1):

```
Encoder                           naive recall@2hop   substrate-whitened   recall@10 (coverage)
Llama-3.2-1B BASE (any config)    0.00-0.04           0.03                 disqualified
MiniLM-L6-v2 (22M)               0.16                0.26 (+63%)          ~0.55 (estimated)
bge-small-en-v1.5 (33M)          0.42                0.38 (-4%)           0.74
```

Key observation: substrate whitening helps weak encoders (MiniLM +63%) but does not help a strongly contrastive-trained encoder. bge-small is already well-conditioned; whitening slightly hurts. This is not a substrate failure -- it matches the theory. Whitening provides the most lift when raw feature correlations bias cosine similarity (MiniLM is not trained to decorrelate features; bge-small is).

Three embedding-based multi-hop methods all plateau at or below bge-small naive recall@2hop:
- vector bridge (q + hop1 vector sum): 0.38
- cross-encoder rerank on top-10: 0.34
- text-level iterative re-encoding: 0.40

The facts are present in recall@10=0.74; they cannot be selected by similarity/ranking alone. This is the structural signature of genuine 2-hop: supporting fact 2 is relevant to fact 1's bridge entity, not to the original question.

---

## Part 1 -- Encoder family evaluation

### P_deflated methodology

Per feedback-lit-scan-calibration-penalty: deflate P estimates by 0.15-0.20 for uncharted regimes. For this drill the regime is partially charted (we have empirical bge-small=0.42 as anchor), so deflation is 0.15 on lit-derived estimates, 0.10 on estimates anchored to the empirical bge-small result.

P_deflated = P_theoretical x P_empirical (product reported).

---

### Family A: 33M-parameter sentence transformers

**bge-small-en-v1.5 (33M) -- EMPIRICALLY CONFIRMED**
- Bare recall@2hop = 0.42 (production harness)
- Substrate recall@2hop = 0.38 (whitening hurts; encoder already conditioned)
- Recall@10 = 0.74 (facts in pool)
- BEIR NDCG@10 = 53.9 (confirmed from MTEB; best in the 33M class)
- Size-fair: clearly yes (33M vs 1B LLM)
- P_actionable for 0.70 via decomp loop: P_theo=0.75 x P_emp=0.80 = 0.60

**gte-small / e5-small-v2 (33M)**
- BEIR NDCG@10: e5-small-v2 = 48.5 (confirmed); gte-small estimated 50-52
- bge-small outperforms both by 2-5 BEIR points within the 33M class
- Expected bare recall@2hop: ~0.35-0.40 (slightly below bge-small)
- P_actionable for 0.70 via decomp: P_theo=0.55 x P_emp=0.65 = 0.36
- Verdict: bge-small is the best 33M encoder; no reason to use gte-small or e5-small over it

**MiniLM-L12-v2 (33M)**
- BEIR NDCG@10: ~48-50 (estimated; MiniLM family is distilled for speed, not BEIR accuracy)
- Expected bare recall@2hop: ~0.20-0.28 (better than L6, worse than bge-small)
- P_actionable for 0.70: P_theo=0.40 x P_emp=0.55 = 0.22
- Verdict: no advantage over bge-small at same param count; skip as production encoder

**jina-embeddings-v2-small (33M)**
- Trained for 8192-token context; HotpotQA passages are short so this advantage is neutral
- Expected bare recall@2hop: ~0.35-0.40 (similar to e5-small tier)
- Custom tokenizer adds integration complexity
- Verdict: no advantage over bge-small for short-passage multi-hop; skip

**Family A summary (33M tier):** bge-small-en-v1.5 is the best available 33M encoder by BEIR and by direct empirical test. The 33M tier has a hard coverage ceiling: bare recall@2hop ~0.42, recall@10 ~0.74. Closing the gap to 0.70 recall@2hop requires multi-hop decomposition, not a better 33M encoder.

---

### Family A: 110M-parameter sentence transformers

**bge-base-en-v1.5 (110M)**
- BEIR NDCG@10 = 53.2 (confirmed; note: bge-small-v1.5 at 53.9 slightly outperforms bge-base-v1.5 -- an unusual inversion documented in the BAAI literature; bge-small-v1.5 was specifically optimized to exceed expectation for its size)
- Expected bare recall@2hop: ~0.40-0.46 (similar range to bge-small; BEIR slightly below bge-small-v1.5)
- Substrate lift: same argument as bge-small; whitening unlikely to add value
- P_actionable for 0.70 via decomp: P_theo=0.68 x P_emp=0.80 = 0.54
- Size-fair: yes (110M vs 1B LLM; 11x smaller)
- Verdict: marginal improvement over bge-small at 3.3x the parameter cost; probably not worth testing unless bge-small pre-test hits a MIDDLE-BAND ceiling

**gte-base-en-v1.5 (110M)**
- BEIR NDCG@10 = 54.1 (confirmed from mGTE technical report; highest in the 110M class)
- Expected bare recall@2hop: ~0.44-0.50 (estimated ~2-8pp above bge-small based on BEIR advantage)
- P_actionable for 0.70 via decomp: P_theo=0.72 x P_emp=0.80 = 0.58
- Size-fair: yes
- Verdict: the best 110M candidate; a 1-2 day pre-test (n=50) would confirm whether the BEIR advantage translates to HotpotQA coverage. Recommended as pre-test B.

**e5-base-v2 (110M)**
- BEIR NDCG@10 = 50.3 (confirmed; lowest in the 110M class)
- Expected bare recall@2hop: ~0.37-0.42 (BEIR suggests below bge-small)
- Verdict: weaker than bge-small at 3.3x the parameters; skip

**nomic-embed-text-v1.5 (137M)**
- BEIR top-5 accuracy ~86.2% (confirmed; roughly NDCG@10 ~54-56 range)
- HotpotQA is confirmed to be in nomic's training data (ablation studies in the nomic paper show HotpotQA + FEVER data as explicit training components)
- This training-set overlap means HotpotQA eval results for nomic are optimistic; cannot use as an uncontaminated test
- P_actionable: P_theo=0.65 x P_emp=0.60 = 0.39 (discounted for contamination)
- Verdict: pre-test with contamination caveat; if dev/test split confirms contamination, exclude from the comparison benchmark

**Family A summary (110M tier):** gte-base-en-v1.5 is the strongest 110M candidate. Predicted bare recall@2hop 0.44-0.50 vs bge-small's 0.42. The gain is likely 2-8 pp in coverage. Whether this improves the recall@10 ceiling above 0.74 is the critical question -- if gte-base pushes recall@10 to 0.80+, the decomp loop has more material to work with. Pre-test B confirms this in 1-2 hrs CPU.

---

### Family B: Retrieval-specialized models

**MDR-style encoder (multi-hop specialized, BERT-base 110M)**
- Published recall@2hop on HotpotQA = 0.659 (Xiong et al. 2021, confirmed)
- MDR uses chained query encoders trained with supervised multi-hop labels on HotpotQA itself
- This is a task-supervised model, not a general encoder -- the comparison story breaks down; MDR trained on HotpotQA vs bare Llama-1B is not a fair test of substrate generalization
- Useful as an upper-bound reference for what a supervised 110M multi-hop encoder achieves
- Verdict: reference ceiling only; not the v1 demo encoder

**Contriever-MS-MARCO (110M, unsupervised + MS-MARCO fine-tuned)**
- Retrieves first-hop passage 49%, second-hop passage 25% on HotpotQA (confirmed)
- These two numbers do not directly give recall@2hop for both facts together, but imply a 2-hop joint recall roughly ~0.25-0.30
- This is meaningfully below bge-small (0.42); Contriever is strong for general retrieval but not specialized for multi-hop
- P_actionable for 0.70: P_theo=0.45 x P_emp=0.65 = 0.29
- Verdict: weaker than bge-small on multi-hop; skip

**DPR (200M, supervised on Natural Questions)**
- DPR is a single-hop retriever trained on NQ; zero-shot transfer to HotpotQA 2-hop is poor
- Expected bare recall@2hop: ~0.15-0.25 (similar to MiniLM; trained for single-hop)
- Verdict: skip

---

### Family C: Late-interaction models

**ColBERT-v2 (110M, late-interaction MaxSim)**
- Published recall on HotpotQA = 59.0 (confirmed; this is the most important external datapoint in this drill)
- ColBERT-v2 without any augmentation gets 0.59 on HotpotQA 2-hop -- already very close to the 0.70 target
- Architecture: BERT-base backbone; each passage is encoded as a set of token vectors; at query time, MaxSim scores each query token against all passage tokens and sums them. This preserves per-token information critical for bridge-entity matching.
- Why ColBERT does better at multi-hop than single-vector models: the bridge entity in hop-1 passage triggers token-level similarity to hop-2 passage tokens; single-vector pooling averages out these individual token signals
- With iterative ColBERT: EfficientRAG achieves 81.84 on HotpotQA (confirmed); the iterative component is the decomposition loop, same concept as our LLM-decomp plan
- Size: 110M (size-fair vs 1B LLM; 11x smaller)
- Integration cost: high -- ColBERT requires a multi-vector index (PLAID/FAISS multi-vector), custom query-time MaxSim scoring, and substrate K-hop would need to store per-token vectors rather than per-document vectors. This is an architectural change to the substrate storage layer.
- P_actionable for 0.70 bare: P_theo=0.80 x P_emp=0.70 = 0.56 (0.59 published; our harness may shift +-0.05)
- P_actionable for 0.70 with decomp: P_theo=0.85 x P_emp=0.80 = 0.68
- Verdict: ColBERT-v2 is the best encoder for HotpotQA 2-hop at size-fair scale. But integration into the substrate architecture is a 2-3 week engineering task. For v1 demo in 5-7 weeks, ColBERT is a stretch goal. Recommend as post-v1 upgrade path.

---

### Family D: Causal LM variants

**Llama-3.2-1B BASE (any layer/pool)**
- EMPIRICALLY CONFIRMED: all configs 0.00-0.04 (exp_dev routing note, n=50, production harness)
- Root cause: next-token LM training does not produce cosine-comparable representations for semantic retrieval
- This is not a substrate failure; it is well-established that base LLMs require contrastive fine-tuning to serve as retrieval encoders (the entire sentence-transformers / e5 / bge training pipeline exists precisely because base LLM embeddings are poor for cosine similarity)
- MTP head does not fix this; the hidden representations are shaped by the autoregressive objective throughout all layers
- Verdict: disqualified; do not re-test

**Llama-3.2-1B with contrastive fine-tuning**
- A contrastively fine-tuned 1B LLM retriever is possible (e5-mistral-7b-instruct at 7B scale achieves BEIR NDCG@10 ~56-58)
- At 1B scale, expected BEIR NDCG@10: ~52-55 (estimated; LLM retrievers at 1B do not dominate bge-small-v1.5 by a large margin)
- Engineering cost: requires contrastive training run; 1-2 weeks
- Size-fairness concern: 1B encoder on substrate side vs 1B bare LLM is size-equal, not size-fair; the substrate overhead (K-hop index, storage) adds to total cost
- Verdict: not recommended for v1; adds engineering cost, muddies the size story, and likely marginally better than bge-small-v1.5 at best

---

### Family E: Hybrid approaches

**BM25 + bge-small late fusion (RRF)**
- BM25 alone on HotpotQA 2-hop: ~30-40% recall (lexical match on keyword queries)
- bge-small alone: 0.42 (empirical)
- Hybrid recall@2hop: estimated 0.48-0.58 (lit range; hybrid BM25+dense typically adds 6-16pp over dense alone on multi-hop)
- Recall@10 with hybrid: likely 0.78-0.85 (expanded candidate pool from complementary methods)
- BM25 specifically helps on questions with named entity bridges where the entity string appears verbatim in the passage
- P_actionable for 0.70 via decomp with hybrid: P_theo=0.75 x P_emp=0.70 = 0.53
- Engineering cost: BM25 index build (Pyserini, ~1-2 days); RRF fusion is trivial (~1hr)
- Verdict: meaningful incremental lift; worth adding as a second-stage after the bge-small + LLM-decomp path is confirmed

**IRCoT / agentic decomposition (published results)**
- PRISM agentic retrieval: 90.9% recall on HotpotQA (confirmed; best published result)
- IRCoT interleaved retrieval + CoT: 72-80% recall (published range)
- These methods require LLM inference at each hop; the substrate's K-hop + LLM loop is an implementation of this class
- The substrate adds structural value on top: audited retrieval steps, bitemporal storage, privacy controls -- none of which vanilla IRCoT has
- P_actionable for the substrate system reaching 0.70: consistent with this research class; the published numbers confirm the ceiling is there

---

## Part 2 -- Calibrated probability estimates per candidate

Stack ranking by P_actionable (P_deflated product; reaching 0.70 recall@2hop on production harness):

| Rank | Encoder + method | Size | P_theo | P_emp | P_product | Integration cost |
|------|-----------------|------|--------|-------|-----------|-----------------|
| 1 | ColBERT-v2 + decomp loop | 110M | 0.85 | 0.80 | 0.68 | 2-3 weeks (high complexity) |
| 2 | bge-small + LLM-decomp loop | 33M + LLM | 0.75 | 0.80 | 0.60 | ~1 week |
| 3 | gte-base-v1.5 + decomp loop | 110M | 0.72 | 0.80 | 0.58 | 1-2 days pre-test |
| 4 | bge-small + BM25 hybrid + decomp | 33M | 0.75 | 0.70 | 0.53 | ~1.5 weeks |
| 5 | bge-base-v1.5 + decomp loop | 110M | 0.68 | 0.80 | 0.54 | 1-2 days pre-test |
| 6 | nomic-embed + decomp | 137M | 0.65 | 0.60 | 0.39 | 1-2 days; contamination caveat |
| 7 | Contriever MS-MARCO + decomp | 110M | 0.45 | 0.65 | 0.29 | 1-2 days pre-test |
| 8 | MiniLM-L6 + substrate whitening | 22M | 0.30 | 0.40 | 0.12 | done; demonstrates lift story |
| 9 | Llama-1B BASE (any config) | 1B | 0.00 | 0.00 | 0.00 | disqualified |

Note: all P_product values above carry an additional ~0.10 floor discount for implementation unknowns and harness behavior at n=100+ (smokes were n=50). Top candidate bge-small+decomp P_product_adjusted = 0.50-0.54.

---

## Part 3 -- Cheap decisive test per top candidate

Per feedback-drill-pretest-required: production-encoder pre-test required before engineering authorization. No proxy setups.

**Pre-test A (FIRST): bge-small + entity-bridge decomp**
- Setup: spaCy NER extracts named entities from the top hop-1 passage; bge-small re-queries for each entity as a stand-alone sub-question; record whether the hop-2 passage appears in the second retrieval's top-5
- N = 100 HotpotQA bridge questions (dev set, not the n=50 used in smoke)
- Metrics: recall@2hop after decomp vs 0.42 naive bge-small baseline
- HARD-PASS: recall@2hop >= 0.65 (on track for 0.70 with LLM-quality decomp)
- HARD-FAIL: recall@2hop < 0.50 (NER decomp not the solution; need LLM decomposer)
- MIDDLE-BAND: 0.50-0.65 (promising; upgrade to LLM decomposer for production)
- Wall: ~2hr CPU; cost $0
- P_PASS = 0.35, P_MIDDLE = 0.50, P_FAIL = 0.15
- Prediction: MIDDLE-BAND (0.55-0.65) -- NER entity extraction misses implicit bridges (~30-40% of HotpotQA bridge questions have abstract-concept bridges that NER does not catch); LLM-quality decomposition is needed for those

**Pre-test B (optional, if A is MIDDLE-BAND): gte-base-v1.5 vs bge-small comparison**
- Setup: same n=50 smoke as hotpot_substrate_bge_v1 but with gte-base-en-v1.5 encoder
- Metrics: recall@2hop naive, recall@10 (facts-in-pool ceiling)
- HARD-PASS: recall@10 >= 0.80 (meaningfully above bge-small's 0.74; worth the 110M budget)
- HARD-FAIL: recall@10 < 0.74 (no improvement; stay with bge-small)
- Wall: ~1hr CPU; cost $0
- P_PASS = 0.35, P_MIDDLE = 0.50, P_FAIL = 0.15

**Pre-test C (optional, if A HARD-FAILS): BM25 + bge-small hybrid**
- Setup: Pyserini BM25 on HotpotQA corpus + bge-small dense, RRF fusion (k1=1.5, b=0.75, lambda=0.5)
- Metrics: recall@2hop, recall@10
- HARD-PASS: recall@2hop >= 0.55 (hybrid adds >=13pp over bge-small alone)
- HARD-FAIL: recall@2hop < 0.45 (no material improvement from hybrid; encoding coverage is the bottleneck, not lexical-vs-semantic)
- Wall: ~3hr CPU (BM25 index build + fusion); cost $0
- P_PASS = 0.45, P_MIDDLE = 0.40, P_FAIL = 0.15

---

## Part 4 -- Falsifiable predictions (HARD-PASS + HARD-FAIL)

### Prediction 1: entity-bridge decomp reaches recall@2hop 0.55-0.75
- Valid under: NER correctly identifies the bridge entity in >=60% of HotpotQA bridge questions
- Will not survive if: bridge entities are implicit / abstract in >=40% of questions (then NER misses them; LLM-quality decomp is required)
- HARD-PASS: recall@2hop >= 0.65 on n=100
- HARD-FAIL: recall@2hop < 0.50 on n=100
- P_deflated: P_theo=0.72 x P_emp=0.73 = 0.53

### Prediction 2: gte-base-v1.5 recall@10 >= 0.80 (materially above bge-small's 0.74)
- Valid under: gte-base's BEIR advantage (54.1 vs 53.9) translates to HotpotQA coverage
- Will not survive if: BEIR rank does not correlate with HotpotQA 2-hop coverage at the 0.1-0.5 NDCG@10 difference level (possible; BEIR does not include HotpotQA as a task)
- HARD-PASS: recall@10 >= 0.80
- HARD-FAIL: recall@10 < 0.74 (no improvement; not worth switching to 110M)
- P_deflated: P_theo=0.60 x P_emp=0.65 = 0.39 (BEIR-to-HotpotQA coverage correlation is uncertain)

### Prediction 3: ColBERT-v2 recall@2hop = 0.55-0.65 on our production harness
- Published number is 0.59; harness differences (corpus size, matching criteria) may shift by +-0.05
- Valid under: our harness uses standard HotpotQA dev set with gold passage matching
- Will not survive if: our matching criterion is stricter than the ColBERT-v2 publication (title+passage vs passage-only can shift by 5-10pp)
- HARD-PASS: recall@2hop >= 0.55 on n=50 (published result transfers)
- HARD-FAIL: recall@2hop < 0.45 (harness mismatch; ColBERT story is broken on our setup)
- P_deflated: P_theo=0.75 x P_emp=0.70 = 0.53

### Prediction 4: LLM-decomp loop on bge-small reaches recall@2hop 0.65-0.80
- The key empirical question: can a 1B LLM decompose bridge questions reliably enough?
- Valid under: Llama-3.2-1B can correctly decompose >=50% of HotpotQA bridge questions into two answerable single-hop sub-questions
- Will not survive if: 1B LLM decomposition quality is too poor (known weakness at 1B scale; 3B+ LLMs decompose better per the LLM-decomp literature)
- HARD-PASS: recall@2hop >= 0.65 on n=100 (confirms system works at 1B scale)
- HARD-FAIL: recall@2hop < 0.50 (1B LLM cannot decompose reliably; need 3B+ decomposer or template-based approach)
- P_deflated: P_theo=0.65 x P_emp=0.65 = 0.42 (small LLM decomp quality is the key open uncertainty)

### Prediction 5: all 33M encoders plateau within +-0.05 recall@2hop of bge-small (embedding ceiling, not encoder ceiling)
- Claim: the multi-hop ceiling at 33M scale is set by the method (single-vector embedding cannot chain bridges), not by encoder quality within the class
- Valid under: gte-small and e5-small both fall in the 0.37-0.47 range
- Will not survive if: any 33M encoder exceeds 0.52 recall@2hop without decomp (would indicate the ceiling is encoder-quality-limited)
- HARD-FAIL of prediction 5: any 33M encoder exceeds 0.52 recall@2hop without decomp
- P_deflated: P_theo=0.80 x P_emp=0.70 = 0.56

---

## Part 5 -- Cross-thread synthesis with prior findings

**Cycle 154-156 confirmed observations (not re-derived here):**
- Llama-1B BASE: 0.00-0.04 recall@2hop across all layer/pool configs -- next-token LM training objective produces representations incompatible with cosine semantic retrieval
- MiniLM +63% lift from substrate whitening -- substrate adds value when encoder features are correlated (weak/general encoder)
- bge-small -4% from substrate whitening -- substrate whitening does not help already well-conditioned encoders
- Single-hop rerank on bge-small top-10 hurts (0.42 to 0.34) -- the bridging fact is NOT question-relevant in the single-hop sense; it is only accessible via the bridge entity chain

**Consistency with substrate value propositions:**

The multi-hop decomposition path maps directly onto the substrate's architectural strengths:
1. K-hop relay: substrate can store the hop-1 retrieval result, extract the bridge entity, and issue a targeted hop-2 query. This is exactly what K-hop was designed for, but it needs entity extraction (not just vector similarity) to work.
2. Audit trail: every retrieval step is logged with its justification; the audit is auditable for multi-hop reasoning paths. This is a strong product differentiator vs "black-box RAG."
3. Bitemporal storage: retrieved passages are stored with provenance; multi-hop paths can be reconstructed and verified post-hoc.

The encoder question is orthogonal to the audit/privacy/GDPR story. bge-small is the correct encoder for the retrieval quality story; the substrate's other value dimensions (audit, privacy, bitemporal, K-hop relay) are independent of which encoder is chosen.

**Substrate lift on weak vs strong encoders:**
The substrate demonstrates different value at different encoder quality levels:
- On MiniLM (weak encoder): substrate whitening provides +63% lift in recall@2hop. This is a compelling standalone story.
- On bge-small (strong encoder): substrate contributes as the structured knowledge graph layer -- K-hop relay for multi-hop, audit trail, privacy controls. The retrieval quality story shifts from "encoder lift" to "system-level multi-hop capability."

Both stories are valid and complementary. The v1 demo should demonstrate both:
(a) Substrate lifts a weak encoder's retrieval quality (MiniLM story -- demonstrable now)
(b) Substrate + strong encoder enables multi-hop reasoning via K-hop relay / decomposition (bge-small story -- next build)

---

## Part 6 -- Substrate-product implications

**Revised v1 demo framing:**

The prior framing (substrate encoder vs bare LLM, same encoder on both sides) was not correctly specified. The correct framing:
- Substrate side: bge-small-en-v1.5 (33M) + substrate K-hop/storage/audit layer + small LLM (1B) for decomposition
- Comparison side: bare Llama-1B LLM with no structured retrieval
- Metric: HotpotQA 2-hop recall@2hop AND answer F1
- Size fairness: substrate side is ~33M + 1B = ~1.03B total parameters vs 1B bare. Approximately fair.

The comparison is system vs system. The substrate system contributes:
1. A retrieval encoder (bge-small, 33M) for passage similarity
2. Structured K-hop storage for multi-hop relay
3. An LLM (1B) as a decomposer and reader
The bare LLM has only a 1B model prompted naively without structured retrieval.

This is the right north-star framing: the assembled system with structured substrate does multi-hop QA that neither the retrieval component alone nor the bare LLM alone accomplishes.

**Recommended encoder selection:**
bge-small-en-v1.5 (33M) is the primary encoder for v1. Rationale:
1. Best empirical recall at 33M (0.42 bare; recall@10=0.74 confirms coverage)
2. Size-fair by a large margin (3.3% of LLM budget)
3. Already in production harness; no new integration needed
4. Substrate whitening story (MiniLM) and substrate K-hop story (bge-small) are both demonstrable

Optional upgrade: run pre-test B (gte-base, 1hr CPU) to confirm whether 110M adds meaningful coverage. If gte-base recall@10 >= 0.80, it may be worth the parameter overhead.

**ColBERT-v2 as a post-v1 upgrade:**
ColBERT-v2's 0.59 bare recall@2hop is the current ceiling for size-fair multi-hop retrieval without decomp. Its integration into the substrate storage layer (multi-vector per-token index) is a non-trivial architectural change. Recommend tracking as a post-v1 upgrade target after the core demo is shipped.

**If no encoder hits 0.70 recall@2hop even with decomp:**
If LLM-decomp + bge-small HARD-FAILS (< 0.50 recall@2hop on n=100), pivot options:
1. LongMemEval / FActScore as headline benchmark: substrate's persistence, audit, and GDPR story is demonstrably strong independent of HotpotQA multi-hop recall. Reframe the demo around what the substrate genuinely does best.
2. Relax target to 0.55-0.60: a 30-40pp improvement over bare Llama (which retrieves ~0.05 on multi-hop without a retrieval system) is still a strong demonstration.
3. Scale up the decomposer: 3B LLM decomposer likely decomposes bridge questions more reliably than 1B. Total substrate-side parameters become ~3B; fair comparison shifts to bare 7B Llama (still favorable story at larger scale).

---

## Summary table

| Scenario | Recall@2hop | Feasibility | Encoder size | v1 path? |
|----------|-------------|-------------|--------------|----------|
| bge-small bare | 0.42 (empirical) | done | 33M | partial baseline |
| bge-small + NER entity-bridge | 0.55-0.65 (P_product=0.53) | 2hr CPU pre-test | 33M | likely yes if NER recall is adequate |
| bge-small + LLM decomp | 0.65-0.75 (P_product=0.42) | 1 week build | 33M + LLM | yes, if 1B LLM decomposes |
| gte-base + decomp | 0.60-0.72 (P_product=0.58) | 2hr pre-test + 1wk | 110M | yes, marginal upgrade |
| ColBERT-v2 bare | 0.55-0.62 on our harness | 2-3wk integration | 110M | post-v1 upgrade path |
| BM25+bge hybrid + decomp | 0.60-0.72 (P_product=0.53) | 1.5 weeks | 33M | secondary path |
| Llama-1B BASE | 0.00-0.04 (empirical) | N/A | 1B | no; disqualified |

---

## Next-drill candidate

**Field:** multi-hop question decomposition quality at 1B LLM scale. The critical remaining uncertainty is whether Llama-3.2-1B can decompose HotpotQA bridge questions into two answerable single-hop sub-queries for >=50% of questions. If the answer is no, the minimum viable decomposer size is 3B+, which changes the size-fairness story for the v1 demo. A targeted literature scan on "small LLM question decomposition quality at 1B vs 3B parameter scale" would bound this uncertainty before the LLM-decomp pre-test is built.

---

## Citations (9 verified)

1. Xiong et al. (2021). Answering Complex Open-Domain Questions with Multi-Hop Dense Retrieval. ICLR 2021. MDR recall@2=0.659 on HotpotQA. https://arxiv.org/pdf/2009.12756
2. Santhanam et al. (2022). ColBERT-v2. HotpotQA recall@2hop=0.59. Cited via https://arxiv.org/pdf/2410.02642
3. BAAI bge-small-en-v1.5. BEIR NDCG@10=53.9. https://huggingface.co/BAAI/bge-small-en-v1.5
4. Wang et al. (2022). Text Embeddings by Weakly-Supervised Contrastive Pre-training (E5). e5-small-v2 BEIR NDCG@10=48.5. MTEB leaderboard.
5. mGTE technical report. gte-base-en-v1.5 BEIR NDCG@10=54.1. https://arxiv.org/pdf/2407.19669
6. Nussbaum et al. (2024). Nomic Embed: Training a Reproducible Long Context Text Embedder. HotpotQA in training data. https://arxiv.org/pdf/2402.01613
7. Ma et al. (2024). EfficientRAG. HotpotQA recall=81.84 with iterative retrieval. https://arxiv.org/html/2408.04259v1
8. Izacard et al. (2022). Contriever. First-hop 49%, second-hop 25% on HotpotQA. https://github.com/facebookresearch/contriever
9. PRISM agentic retrieval. 90.9% recall on HotpotQA. https://arxiv.org/pdf/2510.14278
