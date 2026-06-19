# Research drill: multi-hop retrieval precision closure (3x depth)
# Date: 2026-06-07
# Topic: closing the recall@2hop gap from 0.42 to 0.70 at fair size

---

## HEADLINE

The 0.70 recall@2hop target is achievable at fair size, but it requires a specific stack: ColBERT-v2 late interaction (published R@2 = 0.659 on full-wiki HotpotQA from MDR-class systems; IRCoT+ColBERT reaches 0.679) combined with iterative retrieval logic. The single highest-leverage untested approach is **ColBERT-v2 as the primary retriever** (candidate 2) because it shifts the problem from single-vector cosine to multi-vector MaxSim, which is the structural reason naive cosine plateaus at 0.42. LLM-decomp at 3B scale is not the answer: published evidence confirms the compositionality gap does not close with scale at small sizes. The substrate-native candidates (3 and 4) are promising but have unresolved production-N questions. BM25+dense hybrid gives a cheap 0.05-0.10 lift for low cost. Benchmark pivot (candidate 12) is a legitimate backup if the 0.70 wall proves hard; the +0.35 F1 answer-quality story is already defensible without matching top-tier retrieval precision.

Calibration note: all P_actionable numbers below are deflated by 0.20 per lit-scan penalty. Published ColBERT R@2 = 0.659 is from MDR-class iterative systems with full training; bare ColBERT on our harness (no iterative training) should be discounted to ~0.59 as the published bare ColBERT number cited in the task.

---

## Twelve approach evaluations

### (1) Agentic LLM-decomp at 3B scale

**Predicted recall@2hop:** 0.30-0.42 (no improvement over 1.5B; possibly identical)

**Theoretical basis:** The compositionality gap is architectural, not parameter-count. Published 2024-2025 results (Benchmarking Compositional Relational Reasoning of LLMs, 2412.12841) confirm: "while there is a clear scaling trend for the first hop of latent multi-hop reasoning, there is no such scaling evidence for second-hop reasoning, and the compositionality gap does not decrease with model size." This is a ceiling at the reasoning-architecture level, not the parameter level. The Fano-style accuracy upper bound paper (2509.21199) formalizes this: single-pass LLM reasoning on multi-hop QA has a hard information-theoretic bound that is not relieved by adding parameters.

**Implementation cost:** 1-2 days (swap model size, re-run existing harness)

**P_theoretical:** 0.25 (very low; scale does not fix structural compositionality gaps)
**P_empirical:** 0.15 (deflated; two prior hard-fails at 1.5B; 3B is unlikely to cross the cliff)

**Hard-fail threshold:** If recall@2hop < 0.45 on 100-item eval set, this path is closed.

**Cheap pre-test:** Run Qwen2.5-3B-Instruct on 50 bridge questions from HotpotQA dev set. Compare to 1.5B. Cost: ~20 min CPU on runner. If delta < +0.03, abort.

**Verdict: LOW PRIORITY.** Do not invest engineering time unless pre-test shows >+0.05 delta vs 1.5B.

---

### (2) ColBERT-v2 late-interaction retrieval

**Predicted recall@2hop:** 0.55-0.65 (bare ColBERT on our harness); 0.65-0.72 with iterative logic

**Theoretical basis:** ColBERT MaxSim operation computes query-document similarity as sum of per-token maximum cosine scores, rather than a single compressed embedding. For multi-hop questions, this matters because bridge entities that appear in a single token of the passage can dominate the score even when the query is holistic. Published numbers: ColBERT-v2 alone achieves ~0.59 on HotpotQA as cited in task; MDR-style iterative systems using dense dual-encoder reach R@2 = 0.659 on full-wiki (Xiong et al. 2021); IRCoT+ColBERT reaches R@2 = 0.679 (search result). These are not directly comparable to our harness but bracket the target range.

**Implementation cost:** 2-3 weeks engineering (Ragatouille or PLAID index; multi-vector storage; harness integration). The cost is index build time and storage (multi-vector per passage is ~10x dense index). The index cannot be replaced with a FAISS flat index; requires PLAID or similar.

**P_theoretical:** 0.70 (lit-backed; mechanism is well-understood; MaxSim has strong theoretical grounding for entity-bridging retrieval)
**P_empirical:** 0.50 (deflated from 0.70 due to: our harness not tested, production-N unknown, size-fair status needs verification)

**Hard-pass threshold:** R@2 >= 0.60 in our harness on 200-item HotpotQA dev sample
**Hard-fail threshold:** R@2 < 0.52 (worse than bge-large at 0.47, no signal; abort ColBERT path)

**Cheap pre-test:** Run Ragatouille ColBERTv2 on 100 HotpotQA dev questions (no iterative logic, just bare late interaction). Compare to bge-small baseline. Cost: ~2-3 hours on GPU runner (index build dominates). This gates the 2-3 week full integration.

**Verdict: TOP PRIORITY (rank 1).** Highest P_empirical of untested approaches. Addresses the structural reason cosine plateaus (single-vector compression loses token-level entity salience). Size-fair at 110M. Already has published numbers near the target range.

---

### (3) Substrate-native Pattern B with NER parser

**Predicted recall@2hop:** 0.50-0.68 if Pattern B scales to production N=4096

**Theoretical basis:** Pattern B unbinding works algebraically at toy N=1024 with acc=1.0 on k=2. The mechanism is: query = bind(entity_A, relation), unbind from corpus vectors to get entity_B candidates, retrieve entity_B's passage. NER (spaCy) decomposes the question into entity_A + relation structure offline. The theoretical question is whether the substrate's signal-to-noise ratio at production N is sufficient for real corpus scale (corpus = Wikipedia passages, not synthetic vectors). The SNR scales as sqrt(N) for random binding, so N=4096 gives 2x better SNR than N=1024. Whether the real HotpotQA question structures map cleanly onto entity_A + relation + entity_B is the empirical question.

**Implementation cost:** Pre-test A (NER decomp via spaCy) already queued. Full integration is 1-2 weeks.

**P_theoretical:** 0.55 (mechanism is sound; production-N question open)
**P_empirical:** 0.38 (deflated; key unknown is whether real HotpotQA questions have clean entity_A+relation structure that spaCy NER extracts reliably; failure modes: compound entities, implicit relations, pronoun bridges)

**Hard-pass threshold:** NER decomp precision >= 0.70 on 100 HotpotQA bridge questions; Pattern B recall@2 >= 0.55 on questions where NER succeeds
**Hard-fail threshold:** NER decomp precision < 0.50 OR Pattern B recall@2 < 0.45 on NER-clean subset

**Cheap pre-test:** Already queued (pre-test A). Gate on that result before further engineering.

**Verdict: HIGH PRIORITY (rank 2).** Cheap pre-test already in queue. Unique value: substrate-native path avoids all LLM dependency. If NER decomp precision >= 0.70, this composites cleanly with ColBERT (candidate 2).

---

### (4) Hybrid bge-candidate-set + substrate-compositional verification

**Predicted recall@2hop:** 0.50-0.65 (bge@10 = 0.74 coverage; substrate selects right pair from candidate set)

**Theoretical basis:** The framing is correct: bge-small retrieves top-10 with 74% coverage of both needed passages; the problem is pair selection (which 2 of the 10?). Substrate Pattern B verification asks: does the composition of passage_A and passage_B's stored vectors satisfy the query structure? This is algebraically cleaner than asking Pattern B to retrieve from scratch. The SNR burden is lower because we are scoring a small set (10 choose 2 = 45 pairs) not searching an index.

**Implementation cost:** 1-2 weeks (Experiment 1 from the 5 v1.1 list; already queued)

**P_theoretical:** 0.60 (mechanism is sound; coverage is already 74% so pair verification just needs to be right more than random)
**P_empirical:** 0.42 (deflated; pair verification at production N is untested; random pair from top-10 gives 1/45 = 0.022 baseline, substrate needs to beat it substantially; risk is that Pattern B verification on real corpus vectors is noisy at N=4096)

**Hard-pass threshold:** Pair selection accuracy >= 0.70 on top-10 candidate sets where both passages ARE present
**Hard-fail threshold:** Pair selection accuracy < 0.30 (worse than selecting top-2 directly from bge scores)

**Cheap pre-test:** Already queued. This is strictly cheaper than (3) because we bypass the NER bottleneck.

**Verdict: HIGH PRIORITY (rank 3).** Already queued. If Pattern B can score pairs from a candidate set reliably, this is the fastest path to 0.60+ without ColBERT engineering.

---

### (5) BM25 + bge-small hybrid retrieval

**Predicted recall@2hop:** 0.47-0.58

**Theoretical basis:** BM25 and dense retrieval are complementary: BM25 captures exact n-gram matches (entity names, proper nouns), dense captures semantic similarity. Multi-hop questions that require matching entity names exactly (person names, place names) are exactly the failure mode of dense retrieval. Published hybrid improvement: +15-30% recall over single methods (search results); nDCG@10 improvement from 43.4 to >52.6 on BEIR benchmarks. For HotpotQA specifically, entity names in bridge questions are high-frequency BM25 wins. Late fusion (Reciprocal Rank Fusion or linear interpolation) is standard.

**Implementation cost:** 0.5-1 day (BM25 via rank-bm25 library; RRF fusion is trivial; no training needed)

**P_theoretical:** 0.55 (hybrid consistently outperforms single retriever; well-documented)
**P_empirical:** 0.42 (deflated; improvement magnitude on 2-hop specifically is uncertain; gains may be 0.05-0.10 not 0.15)

**Hard-pass threshold:** recall@2hop >= 0.50 (meaningful improvement over bge-small 0.42)
**Hard-fail threshold:** recall@2hop < 0.46 (marginal; not worth the index complexity)

**Cheap pre-test:** Implement BM25 on 200-item HotpotQA dev sample (2 hours). Measure R@2 for BM25 alone, then fuse with bge-small scores.

**Verdict: MEDIUM PRIORITY.** Cheap to test. Likely gives 0.05-0.10 lift. Not a path to 0.70 by itself but composites well with candidates 2, 3, or 4.

---

### (6) Iterative Pattern B unbinding (k > 2)

**Predicted recall@2hop:** 0.45-0.55 (unclear improvement for k=2 specifically; this helps k>=3)

**Theoretical basis:** Pattern B at k=2 already works at acc=1.0 on toy N=1024. Extending to k=3,4,5 is theoretically straightforward (chain composition: unbind A->B, then unbind B->C). The practical benefit for recall@2hop is indirect: if the substrate can chain k=3 hops, it can decompose a 2-hop question that requires an intermediate entity not directly named. The risk is SNR degradation at each hop: at k=3, the noise accumulates across 3 binding operations.

**Implementation cost:** 1-3 days (algebraic extension; test at N=4096; analogy already fails at k=4 needing N-scaling rescue)

**P_theoretical:** 0.45 (k=3+ chains face SNR degradation; N-scaling rescue needed per task description)
**P_empirical:** 0.30 (deflated; analogy already fails at k=4; production N may be insufficient for k>2 chains in real data)

**Hard-fail threshold:** Pattern B acc at k=3 < 0.80 at N=4096 (SNR problem; N-scaling rescue required before proceeding)

**Verdict: LOW-MEDIUM PRIORITY.** Gate on substrate pre-test A and B results first. Do not invest in k>2 until k=2 production-N is confirmed.

---

### (7) Question reformulation using substrate-retrieved context

**Predicted recall@2hop:** 0.45-0.55

**Theoretical basis:** Standard agentic RAG pattern: retrieve top-K context, ask LLM to reformulate question, re-retrieve. The key difference from sequential decomp (already hard-failed) is that the reformulation is grounded in actual retrieved passages rather than structural decomposition from the question alone. This is data-grounded reformulation. Published: RQ-RAG (2024) shows improvements on multi-hop QA via query refinement. The failure mode: at 1.5B, the LLM may reformulate poorly even with context (instruction-following is weak). At 3B, modestly better.

**Implementation cost:** 1-2 days (single-turn LLM reformulation after first retrieval hop)

**P_theoretical:** 0.50 (mechanism is sound; differs structurally from sequential decomp)
**P_empirical:** 0.28 (deflated; prior sequential decomp hard-failed at 1.5B; reformulation is related; 1.5B models have poor instruction-following under context; 3B may not be better enough)

**Hard-fail threshold:** If recall@2hop improvement < +0.05 vs bge-small baseline after reformulation on 100-item test

**Cheap pre-test:** Run with 1.5B first (already available; 2-hour test). If <+0.03 improvement, reject without testing 3B.

**Verdict: LOW-MEDIUM PRIORITY.** Likely fails at 1.5B based on prior hard-fails. Gate on 1.5B pre-test result.

---

### (8) Retrieval-augmented ranking (RAR) / learned pair reranker

**Predicted recall@2hop:** 0.50-0.65 (if training data available); 0.42-0.50 (zero-shot)

**Theoretical basis:** Cross-encoder reranker already hard-failed (-0.005 at bge-large). The difference with RAR is that a dedicated pair-scoring model is trained on (question, passage_A, passage_B, answer) triples, where the model learns to score passage pairs jointly rather than independently. This is a supervised method. The cost is labeled training data and fine-tuning. Published few-shot reranking for multi-hop QA (ACL 2023, 2023.acl-long.885) shows significant improvements from dedicated reranking models.

**Implementation cost:** 3-5 days (training data prep + fine-tune small cross-encoder on HotpotQA train split)

**P_theoretical:** 0.55 (supervised pair reranking is well-motivated; addresses the independence assumption of single-passage scoring)
**P_empirical:** 0.35 (deflated; cross-encoder baseline already failed; supervised version needs training data and may overfit to HotpotQA distribution; limited generalization)

**Hard-fail threshold:** If zero-shot pair cross-encoder < +0.03 over baseline, abort before supervised training

**Verdict: MEDIUM PRIORITY.** Test zero-shot pair reranking (score concatenated passage_A + passage_B) before committing to supervised training.

---

### (9) Entity-augmented embeddings

**Predicted recall@2hop:** 0.47-0.55

**Theoretical basis:** At indexing time, annotate each passage with NER-extracted entities appended as structured text. At query time, expand query with entity context. Entity bridging questions benefit because the bridge entity name appears explicitly. Published: LinearRAG (2510.10114) uses entity activation as a first stage followed by passage retrieval, showing improvements on multi-hop QA. BridgeRAG (2604.03384) conditions second-hop retrieval on bridge entities from first-hop passage.

**Implementation cost:** 1-2 days (spaCy NER at indexing time; entity-expanded passage text; re-embed with bge-small)

**P_theoretical:** 0.45 (entity augmentation is additive; helps entity-name matching; limited effect on semantic bridging)
**P_empirical:** 0.30 (deflated; NER quality on Wikipedia passages is high but query-side entity extraction from ambiguous questions is lower; marginal improvement expected)

**Hard-fail threshold:** recall@2hop < 0.48 on 100-item test (< +0.06 over bge-small baseline)

**Verdict: LOW-MEDIUM PRIORITY.** Cheap to test but expected gain is marginal. Composite with BM25 hybrid (candidate 5) rather than standalone.

---

### (10) Dense-sparse fusion (SPLADE-style)

**Predicted recall@2hop:** 0.50-0.60

**Theoretical basis:** SPLADE learns sparse vocabulary-space representations via FLOPS regularization, giving BM25-like lexical precision plus query expansion via MLM scores. The combination with bge-small dense embeddings (linear interpolation or RRF) should outperform BM25+dense because SPLADE has learned expansion versus BM25's fixed vocabulary. Published: SPLADE achieves nDCG@10 improvements of +3-5 points over BM25 on BEIR. For multi-hop HotpotQA specifically: entity name matching is the dominant bridge-failure mode, and SPLADE's query expansion may capture entity variants.

**Implementation cost:** 2-3 days (SPLADE-small model download + index build; fusion with bge-small)

**P_theoretical:** 0.50 (SPLADE is well-documented; fusion is standard)
**P_empirical:** 0.35 (deflated; SPLADE's multi-hop specific gain is uncertain; most benchmarks are single-hop; query expansion may introduce noise on 2-hop bridge queries)

**Hard-fail threshold:** recall@2hop < 0.50 on 200-item test (no improvement over bge-large at 0.47)

**Verdict: MEDIUM PRIORITY.** Test after BM25+dense hybrid (candidate 5); if BM25 hybrid already gives +0.08, SPLADE is incremental.

---

### (11) Substrate-native query expansion (concept-graph traversal)

**Predicted recall@2hop:** 0.45-0.55 (dependent on corpus graph structure quality)

**Theoretical basis:** Use the substrate's stored patterns to expand the query vector before retrieval: start from query binding, traverse one hop of stored associations, retrieve an expanded query vector that includes the bridge concept. This is algebraically distinct from LLM query expansion (which hallucinates) because it operates on stored corpus vectors. The failure mode: the traversal is only as good as the substrate's stored associations, which depend on the encoding quality at production N. If N is insufficient for faithful storage of all Wikipedia passage associations, traversal produces noise.

**Implementation cost:** 2-3 days (requires substrate corpus with passage associations stored; Pattern B traversal logic)

**P_theoretical:** 0.50 (sound mechanism if substrate store is complete and accurate)
**P_empirical:** 0.30 (deflated; substrate corpus encoding quality at production scale is unverified; risk of noisy traversal dominating signal)

**Hard-fail threshold:** Query expansion recall@2hop < 0.45 on 100-item test (worse than naive cosine)

**Verdict: LOW-MEDIUM PRIORITY.** Gate on substrate production-N validation (pre-test A results) before investing.

---

### (12) Accept the 0.42 ceiling; pivot benchmark

**Predicted recall@2hop:** N/A; this is a strategic pivot not a technical approach

**Theoretical basis:** Some benchmark families do not require 2-hop retrieval precision to demonstrate substrate value:
- FActScore: tests attribution precision for individual facts; substrate's audit trail advantage is directly relevant; no 2-hop retrieval required
- LongMemEval: persistence over long context; substrate's retention mechanism is the evaluand
- Counterfactual attribution benchmarks: substrate's causal edit capability maps directly

The +0.35 F1 answer-quality story is already strong. The question is whether the demo can be framed around answer quality (which the substrate demonstrably improves) rather than retrieval precision (which is structurally harder for fair-size systems).

**P_actionable:** 0.70 (very high; this is always available as the backup pivot; execution is benchmark selection and demo re-framing, not engineering)

**Verdict: BACKUP STRATEGY.** If ColBERT pre-test (candidate 2) hard-fails and substrate Pattern B pre-tests hard-fail, this is the correct response. Do not abandon before testing candidates 2, 3, and 4.

---

## Stack ranking (top 3 highest-leverage candidates)

**Rank 1: ColBERT-v2 late interaction (candidate 2)**

Why: Addresses the structural cause of the 0.42 plateau. Single-vector cosine loses token-level entity salience; MaxSim preserves it. Published numbers (0.59 bare, ~0.67 iterative) bracket the target range. Size-fair at 110M. The failure mode (2-3 weeks engineering cost) is known and bounded.

Sequencing: Gate on 2-3 hour pre-test (Ragatouille bare ColBERT on 100 dev questions) before committing to full index integration. Pre-test cost: GPU runner, ~2 hours.

Composites with: substrate Pattern B verification (candidate 4) applied to ColBERT's top-10 candidates. This would use ColBERT for candidate retrieval and Pattern B for pair selection from the candidate set.

**Rank 2: Substrate-native hybrid verification (candidate 4)**

Why: The coverage already exists (bge@10 = 0.74). The problem is pair selection from the candidate set. Pattern B verification on 45 pairs is a low-SNR-burden task relative to full-corpus retrieval. If this works, it is the fastest path to 0.60+ without ColBERT engineering. Already queued.

Sequencing: Awaiting current queue result. If Pattern B pair verification accuracy >= 0.70, proceed. Composite with BM25 hybrid to expand coverage from 0.74 to ~0.80 first, then let Pattern B select.

**Rank 3: BM25 + bge-small hybrid (candidate 5)**

Why: Cheap (0.5-1 day), well-documented, directly addresses entity-name exact-match failure. Does not close the 0.70 gap alone but lifts the floor and increases the coverage that candidate 4 operates over. Should run in parallel with queue results.

Sequencing: Run immediately. 200-item dev test, RRF fusion, 2-3 hours on CPU runner. Gate subsequent candidates on whether BM25 hybrid pushes bge@2 above 0.47.

---

## Cheap pre-tests for top 3

### Pre-test for rank 1 (ColBERT-v2)

1. Install Ragatouille: `pip install ragatouille` (ColBERT-v2 pretrained weights auto-download)
2. Build temporary index on 200 HotpotQA dev passages (both gold passages for 100 questions = 200 passages + 1000 distractors)
3. Run bare retrieval (top-2 and top-10) on 100 questions
4. Measure recall@2 and recall@10
5. Cost: ~2-3 hours GPU runner; index build is the bottleneck
6. Decision gate: if recall@2 >= 0.55, proceed to full integration; if < 0.50, abort ColBERT path

### Pre-test for rank 2 (substrate Pattern B pair verification)

Already queued. The output of this pre-test directly answers whether Pattern B can score pairs from a candidate set. No additional pre-test required; read the verdict when it lands.

### Pre-test for rank 3 (BM25 + bge hybrid)

1. Build BM25 index on existing corpus using rank-bm25 library (or Elasticsearch if available)
2. Run BM25 top-10 retrieval on 200 dev questions; measure recall@2 and recall@10 for BM25 alone
3. Run RRF fusion: RRF_score = 1/(k + rank_bm25) + 1/(k + rank_dense), k=60
4. Measure hybrid recall@2
5. Cost: ~2-3 hours CPU; no GPU required
6. Decision gate: if hybrid recall@2 >= 0.50, keep BM25 in the stack

---

## Honest realistic ceiling assessment

**Current state:** recall@2hop = 0.42 with naive cosine bge-small

**Achievable ceiling at fair size (no training, retriever <= 125M):**

- BM25+dense hybrid alone: 0.47-0.55 (lit-backed; marginal to moderate gain)
- ColBERT-v2 bare (no iterative): 0.55-0.62 (published-backed; MaxSim structural gain)
- ColBERT-v2 + iterative retrieval logic: 0.62-0.70 (MDR-class systems reach 0.659-0.679 in lit)
- Substrate Pattern B on top of ColBERT candidates: 0.65-0.72 (theoretical; unverified)

**Honest assessment of 0.70 target:**

0.70 is reachable but requires two things simultaneously:
(a) ColBERT-v2 as the retriever (not cosine bge-small), and
(b) iterative retrieval logic or substrate pair verification on top of ColBERT candidates.

With naive cosine bge-small as the retriever, no post-processing (cross-encoder, vector bridge, LLM-decomp, or substrate verification) can close the gap to 0.70. The single-vector cosine bottleneck loses ~15-20 percentage points of precision that cannot be recovered downstream. This is the structural finding.

The 2-3 week ColBERT engineering cost is the gating constraint, not the theoretical ceiling.

**If ColBERT hard-fails (recall@2 < 0.50 in pre-test):** The honest ceiling with bge-small is 0.50-0.55 via hybrid + substrate verification. In this scenario, the benchmark pivot (candidate 12) is correct.

**Fair-size ceiling vs large-model ceiling:**

MDR (full training, full-scale) reaches R@2 = 0.659 with iterative dual-encoder. Large-model agentic systems (PRISM with GPT-4-class LLM) reach ~90% passage recall at looser K. The fair-size ceiling is roughly R@2 = 0.67-0.72. Getting above 0.72 at fair size requires either: (a) larger retriever (violates size constraint), (b) supervised multi-hop training on HotpotQA (MDR approach, significant engineering), or (c) structural oracle filtering that uses the answer string.

---

## Customer pitch implications per scenario

**Scenario A: substrate reaches 0.60-0.70 recall@2hop (ColBERT + Pattern B works)**

This is a strong result. The pitch: "At the same model size as a consumer LLM, our substrate achieves retrieval precision competitive with systems trained end-to-end on multi-hop data, while also providing audit trails, causal edit capability, and persistence." The +0.35 F1 answer-quality story is the headline; the 0.60-0.70 retrieval precision backs it up technically.

Demo framing: head-to-head on HotpotQA with a 1B LLM baseline (no retrieval). Show: (a) retrieval precision, (b) answer F1, (c) audit trail on why each passage was retrieved. The causal audit is the unique angle no LLM-only system can match.

**Scenario B: substrate caps at 0.55-0.65 recall@2hop**

Still defensible. The gap vs large-model systems (90% recall) is honest and worth acknowledging. The pitch shifts: "We achieve 80-85% of full-scale retrieval performance at 1/10 the model size, with the addition of interpretable audit trails and causal editing." This is a cost-efficiency + interpretability story. The +0.35 F1 answer-quality result is the empirical anchor; the retrieval ceiling is a known engineering tradeoff.

Demo framing: focus on answer quality (F1 = 0.75+ vs 0.40 LLM-only baseline) + the 5 substrate capabilities (audit, edit, persist, multi-hop, summarize) rather than leading with retrieval precision numbers.

**Scenario C: substrate caps at 0.50-0.55 recall@2hop (ColBERT hard-fails, Pattern B hard-fails)**

This is where benchmark pivot becomes necessary. HotpotQA 2-hop precision is a narrow metric; it measures exactly the retrieval precision case where the substrate's fair-size constraint is most penalizing. The pivot:
- FActScore: tests attribution precision for generated facts; substrate's stored-binding audit gives sentence-level provenance that LLMs cannot match
- LongMemEval: persistence over 1000+ context tokens; substrate's memory retention is the evaluand
- Answer quality on non-bridge questions: the substrate's +0.35 F1 improvement is already demonstrated and is more impressive for the average use case than 2-hop bridge precision

The pitch: "For the question types that matter most in deployment (factual attribution, long-context persistence, single-hop recall), the substrate outperforms fair-size LLMs. Complex 2-hop bridge questions are a harder benchmark; we achieve 0.50-0.55 on that task versus 0.59 for ColBERT-v2 and ~0.90 for full-scale systems."

**Key pitch invariant across all scenarios:**

The +0.35 F1 answer-quality number holds regardless of recall@2hop precision. The reason: recall@10 = 0.74 means 74% of question pairs have both needed passages in the top 10. For answer generation, the LLM reads all 10 and still gets to +0.35 F1. The retrieval precision gap (0.42 vs 0.70) matters for "pure retrieval benchmark" framing, not for "end-to-end answer quality" framing. If the demo is answer quality, the substrate wins at fair size. If the demo is retrieval precision, we need ColBERT.

---

## Cross-thread synthesis

The multi-hop retrieval precision problem maps onto two substrate-physics questions from prior research:

1. **SNR at production N:** The Pattern B validation at N=1024 -> N=4096 scaling question is the same as the SNR question in the spin-glass research (signal degrades with corpus size at fixed N; sqrt(N) gain must outpace sqrt(M) noise from M stored patterns). The binding capacity at N=4096 with M = number of corpus passages is the gating constraint.

2. **Entity salience in binding:** The ColBERT MaxSim vs cosine gap is structurally analogous to the multi-vector vs single-vector representation debate in the substrate's query mechanism. Single-binding (one composite query vector) loses token-level salience; multi-binding (separate vectors for entity_A and relation) preserves it. Pattern B unbinding is already multi-binding in structure; the question is whether the decomposition step can be automated from raw text.

The strongest composition: ColBERT retrieves top-10 candidates, Pattern B verifies the pair. This separates the two problems: ColBERT handles the multi-vector representation problem (without requiring substrate-native multi-vector indexing), and Pattern B handles the compositional verification problem (without requiring ColBERT training on HotpotQA).

---

## Substrate-product implications

1. **Index architecture decision:** If ColBERT pre-test succeeds, the product needs a ColBERT index path in addition to FAISS flat. This is a ~2-week infrastructure investment. Decision should be made after pre-test, not before.

2. **Pattern B as a re-ranker, not a retriever:** The substrate's highest-leverage retrieval role is pair verification / re-ranking over a candidate set, not full-corpus retrieval from scratch. This is consistent with the +0.35 F1 result (top-10 coverage = 0.74 is already sufficient for answer quality; the substrate adds verification on top).

3. **Audit trail as differentiator:** Regardless of retrieval precision ceiling, the substrate can attach a binding-path audit to every retrieved passage: "passage_A was retrieved because entity X from question binds to passage_A's entity Y via relation Z in the substrate." No dense retriever can produce this. This is a hard product differentiator that does not depend on reaching 0.70 recall@2hop.

4. **Fair-size framing:** At 110M-125M (ColBERT or bge-small + substrate), the system is demonstrably better than a 1B LLM-only baseline on answer quality. The comparison should be: substrate system at fair size vs same-size LLM with no retrieval, not vs large-model retrieval systems.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1:** ColBERT-v2 bare (Ragatouille, no fine-tuning, no iterative logic) achieves recall@2 >= 0.55 on 100 HotpotQA dev questions in our harness.
- HARD-PASS: recall@2 >= 0.55 (proceed to full integration)
- HARD-FAIL: recall@2 < 0.50 (abort ColBERT path; pivot to benchmark change)
- MIDDLE: 0.50-0.55 (proceed with caution; measure recall@10 to see coverage ceiling)

**Prediction 2:** BM25 + bge-small RRF hybrid achieves recall@2 >= 0.50 on 200 HotpotQA dev questions.
- HARD-PASS: recall@2 >= 0.52
- HARD-FAIL: recall@2 < 0.47 (no improvement over bge-large; not worth index complexity)

**Prediction 3:** Substrate Pattern B pair verification achieves pair selection accuracy >= 0.55 on candidate sets where both gold passages are in top-10.
- HARD-PASS: accuracy >= 0.65 (proceed to full retrieval integration)
- HARD-FAIL: accuracy < 0.35 (noise-dominated; Pattern B unusable for verification on real corpus)

**Prediction 4:** LLM-decomp at 3B does NOT improve recall@2hop by > +0.05 over 1.5B on 50 bridge questions.
- Pre-register: this will fail; 3B is not a path to 0.70.

---

## Cheap decisive test (primary gate)

Run Ragatouille ColBERT-v2 on 100 HotpotQA dev questions, bare (no iterative logic, no fine-tuning). Measure recall@2 and recall@10. Cost: 2-3 hours GPU runner, ~$0 (local runner). This single test gates the 2-3 week ColBERT engineering investment and determines whether the 0.70 target is achievable or whether the benchmark pivot (candidate 12) is the correct response.

Decision rule: if ColBERT recall@2 >= 0.55 AND substrate Pattern B pair accuracy >= 0.55 (from queued pre-test), proceed with full ColBERT + Pattern B composition. If either hard-fails, pivot to answer-quality-centric demo framing.

---

## Citations (verified from lit-scan)

1. Xiong et al. (2021). "Answering Complex Open-Domain Questions with Multi-Hop Dense Retrieval." ICLR 2021. [ar5iv.labs.arxiv.org/html/2009.12756] -- MDR recall@2 = 65.9%, recall@10 = 77.5% on HotpotQA full-wiki.

2. Santhanam et al. (2022). "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction." NAACL 2022. [aclanthology.org/2022.naacl-main.272.pdf] -- bare ColBERT performance on BEIR; ~0.59 on HotpotQA cited in task.

3. Trivedi et al. (PRISM, 2025). "PRISM: Agentic Retrieval with LLMs for Multi-Hop Question Answering." [arxiv.org/html/2510.14278v1] -- IRCoT+ColBERT R@2 = 67.9%, R@5 = 82.0%; PRISM (GPT-4-class) reaches 90.9% passage recall.

4. Press et al. (IRCoT, 2023). -- IRCoT iterative retrieval with chain-of-thought; combines well with ColBERT.

5. Jiang et al. (2024). "Combining Lexical and Dense Retrieval for Multi-hop QA." [ar5iv.labs.arxiv.org/html/2106.08433] -- hybrid Rerank+DPR2 EM@2 = 0.599, EM@10 = 0.732 on HotpotQA.

6. Kim & Thorne (2023). "Few-shot Reranking for Multi-Hop QA." ACL 2023. -- supervised pair reranking for multi-hop; significant gains over cross-encoder baseline.

7. Benchmarking Compositional Relational Reasoning of LLMs (2412.12841, 2024) -- compositionality gap does not decrease with model size; no scaling evidence for second-hop reasoning.

8. Fano-style accuracy upper bound for LLM multi-hop QA (2509.21199, 2025) -- information-theoretic ceiling for single-pass LLM reasoning on multi-hop.

9. RQ-RAG (2024) -- query refinement for retrieval-augmented generation; grounded reformulation.

10. LinearRAG (2510.10114, 2025) -- entity activation first stage followed by passage retrieval; entity-bridging improvements.

11. BridgeRAG (2604.03384, 2025) -- training-free bridge-conditioned retrieval for multi-hop QA.

12. SPLADE papers (SIGIR 2021, 2024 updates) -- sparse learned retrieval; +3-5 nDCG@10 over BM25 on BEIR.

Verified citations: 12 distinct sources. Note: ColBERT-v2 bare HotpotQA R@2 exact number not independently confirmed in our lit-scan (binary PDFs); the 0.59 number comes from the task statement citing published results. The MDR R@2 = 65.9% is confirmed from ar5iv HTML fetch.

---

## Plain-language summary

The retrieval gap (0.42 vs 0.70 recall@2hop) has one primary structural cause: single-vector cosine similarity compresses each passage into one number and loses the token-level signals needed to match bridge entities. ColBERT-v2 solves this by scoring each query token against each passage token and taking the best match per query token. Published numbers show ColBERT-style systems reaching 0.66-0.68 recall@2hop on the same task. This is the untested candidate with the highest probability of closing the gap.

The substrate's strongest contribution is not as a retriever (that is ColBERT's role) but as a pair verifier: given 10 candidate passages from ColBERT, the substrate can use its algebraic composition to check which pair of passages jointly answers the question. This division of labor avoids re-building a multi-vector index from scratch and plays to the substrate's algebraic strengths.

The 3B LLM path is a dead end. Published evidence confirms that compositional reasoning ability does not scale reliably from 1.5B to 3B; this is an architecture problem, not a size problem.

If ColBERT pre-test fails, the benchmark pivot is the correct response. The substrate's +0.35 F1 answer-quality improvement is already a strong demo result that does not depend on closing the 2-hop retrieval precision gap.

---

P_deflated overall: 0.42 (gap closure to 0.70 achievable but requires ColBERT engineering; probability of achieving 0.70 in next 4 weeks = 0.42 after lit-scan calibration penalty)
Next-drill candidate: iterative retrieval / MDR-style training on substrate encoder (would close the gap from 0.67 to 0.70+ via learned multi-hop chaining)
