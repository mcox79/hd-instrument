# Research drill: substrate value-add on strong sentence encoders (3x)
**Date:** 2026-06-07
**Trigger:** Empirical result cycles 156-157 showing K-hop + whitening hurt bge-small recall by 2.7%; MiniLM lifted +33%. Task: map 10 candidate axes where substrate may still add value on strong encoders.

---

## HEADLINE

K-hop graph chaining is encoder-strength-gated: it fills in gaps a weak encoder leaves on the table, but gets in the way when a strong encoder has already found the right documents. This is the correct diagnosis. The substrate has 9 other axes where it may add measurable or structural value regardless of encoder quality. Three are pre-testable in 1-2 CPU hours. Four are compliance/distributed properties that benchmarks do not capture. The customer pitch needs to split: retrieval-F1 pitch (encoder-specific, only valid on weak encoders) vs. robustness + compliance pitch (encoder-independent, valid everywhere).

---

## Cheap decisive test

Run 3 cheap CPU pre-tests in sequence:

1. **Adversarial robustness pre-test** (2h CPU): inject 6 attack-class adversarial passages into a 10K bge-small indexed KB. Measure retrieval recall@10 under attack with and without the substrate confidence filter T=0.5 + hallucination AUC check. PASS: filter reduces adversarial rank injection by >= 30%. FAIL: <= 10% reduction.

2. **Noise robustness pre-test** (1h CPU): add Gaussian noise std=0.20 to stored bge-small embeddings at N=10K. Compare recall@10 with H=1 (bge alone) vs H=2 BFT voting. PASS: H=2 gives >= 5% recall lift under noise. FAIL: <= 1% lift.

3. **Compositional precision pre-test** (2h CPU): on 100 2-hop questions, use bge-small top-10 as the candidate pool, then apply substrate Pattern B compositional reranker (role-filler binding). Measure precision@3 vs. bge-small top-3 baseline. PASS: >= 15% precision gain. FAIL: <= 5% gain.

---

## 10-Axis evaluation

### Axis 1: Adversarial robustness

**What it is:** A pre-calibrated confidence filter (T=0.5) plus hallucination detection (cycle 145 KF-1) catches adversarially injected passages before they rank.

**Empirical state:** Cycle 145 showed AUC 0.96-0.97 on 6 attack classes on the substrate's own retrieval path. No published benchmark directly compares a strong encoder (bge) + adversarial defense against bge alone.

**Lit-scan finding:** Published work (arxiv 2407.06992, survey) confirms strong encoders ARE still vulnerable to corpus poisoning, backdoor attacks, and encoding attacks. Defense requires active mechanisms (adversarial training, detection layers), not just encoder quality. bge/E5 do not ship with built-in adversarial detection.

**Assessment:** EXISTS but NOT YET TESTED in head-to-head bge vs bge+substrate configuration. The substrate filter algebra is encoder-agnostic; it operates on the retrieved document set, not on the encoder vectors. This means it should transfer to bge-small outputs without modification.

**P_theoretical:** 0.70 (the filter operates on the retrieved document set, not on encoder vectors; encoder-agnostic)
**P_empirical (pre-test not yet run):** 0.55
**P_deflated:** 0.48 (calibration penalty applied)
**HARD-PASS threshold:** >= 30% reduction in adversarial rank injection in the pre-test
**HARD-FAIL threshold:** <= 10% reduction -- filter is not catching adversarial documents reliably enough to be a product feature

---

### Axis 2: Noise robustness (H=2 BFT voting)

**What it is:** Multi-head H=2 Byzantine fault tolerant voting over retrieval candidates. Validated in CELL-4 at 100K facts with perfect recall up to noise std=0.50.

**Empirical state:** CELL-4 result is on the substrate's own encoding path. Whether H=2 BFT on top of bge-small embeddings also gives recall protection is untested.

**Lit-scan finding:** Published RAG robustness literature (arxiv 2506.00054, 2507.06956) focuses on positional perturbation robustness and query-level noise, not embedding-space noise. BFT ensemble voting over retrieval sets has limited published precedent in the RAG context (SelectVote 2025 is the closest analog, focused on evidence custody). RAG-Fusion (multi-query reciprocal rank fusion) is the nearest published analog and has demonstrated recall gains. The math of majority-vote variance reduction is well-established; the question is whether bge-small embeddings show enough noise under realistic conditions to make the defense worth enabling.

**Assessment:** EXISTS. Mechanism partially different from RAG-Fusion (embedding-level voting vs multi-query voting), but algebraically compatible. Pre-test is cheap (1h CPU).

**P_theoretical:** 0.65 (majority vote over multiple retrieval heads is a known variance-reduction technique)
**P_empirical (pre-test not yet run):** 0.50
**P_deflated:** 0.45
**HARD-PASS threshold:** >= 5% recall lift under embedding noise std=0.20
**HARD-FAIL threshold:** <= 1% lift -- voting does not help when bge embeddings are already highly stable

---

### Axis 3: Compositional precision reranking (Pattern B)

**What it is:** Substrate Pattern B uses VSA role-filler binding to extract structured predicates from bge-small top-10 candidates and rerank by compositional match to a structured query. Substrate does NOT replace bge's ranking -- it operates as a precision filter on top of it.

**Empirical state:** Cycle 153 causal HP passed, validating the compositional algebra. Integration with bge-small as the upstream retriever is not yet run.

**Lit-scan finding:** Multi-hop compositional retrieval literature (Hierarchical Lexical Graph 2506.08074, PRISM 2510.14278, KG-CQR 2508.20417) consistently shows that neural rerankers with structured information outperform pure embedding similarity for multi-hop and relational queries. The substrate's approach (structured reranking from bge-small pool) is architecturally compatible with recent best practice. MuSiQue (2-4 hop compositional QA) is the benchmark where this axis can be tested.

**Assessment:** EXISTS, well-supported by lit, cheap to pre-test. The biggest risk is SRL accuracy on domain text (flagged in earlier drill: 70-80% on specialized domains).

**P_theoretical:** 0.60 (compositional reranking algebra is sound; precision@3 should improve when structure is present)
**P_empirical (pre-test not yet run):** 0.50
**P_deflated:** 0.42
**HARD-PASS threshold:** >= 15% precision@3 gain on 2-hop questions vs bge-small alone
**HARD-FAIL threshold:** <= 5% gain -- structured reranking does not add signal beyond bge-small similarity

---

### Axis 4: Hallucination resistance (confidence filter layer)

**What it is:** Substrate's T=0.5 confidence filter rejects low-confidence retrievals before they reach the LLM context window. Hallucination detection AUC ~0.97 (cycle 145).

**Empirical state:** Validated on substrate's own retrieval path. Whether it adds measurable anti-hallucination protection when applied to bge-small outputs is untested.

**Lit-scan finding:** RAG hallucination detection literature (FACTUM 2601.05866, RAGLens, RAGAS, 2506.06240) confirms that most detection requires either LLM internal activations or retrieved-vs-generated alignment. The substrate's confidence filter is a retrieval-side threshold -- it prevents hallucination-prone retrievals from entering context rather than detecting post-generation. Published work does not have a direct analog for retrieval-side confidence gating on top of a strong encoder; this is a distinct (earlier-in-pipeline) mechanism.

**Assessment:** PARTIALLY TESTED on substrate's path. Pre-test is bundled with Axis 1 (same adversarial pre-test setup includes hallucination AUC measurement).

**P_deflated:** 0.40
**HARD-PASS threshold:** >= 20% reduction in false-positive hallucinated retrievals vs no filter
**HARD-FAIL threshold:** <= 5% reduction

---

### Axis 5: Audit trail and provenance (Merkle per retrieval)

**What it is:** Every retrieval event is cryptographically logged with a Merkle proof linking the retrieved passage to its ingestion event. Strong encoders do not provide this.

**Empirical state:** Architecture is implemented. No head-to-head benchmark exists comparing Merkle-logged vs. unlogged retrieval on any standard metric (because no standard metric captures this).

**Lit-scan finding:** Privacy-preserving RAG literature (arxiv 2412.04697, 2601.03979) focuses on differential privacy and membership inference, not on audit trails. EU AI Act Article 12 (August 2026 compliance deadline) requires traceability of AI system outputs. No RAG benchmark currently measures audit trail completeness.

**Assessment:** STRUCTURAL VALUE ONLY. This axis will not appear in any retrieval benchmark (recall@K, MRR, NDCG). It is real and legally mandated for regulated industries, but benchmarks do not test it. Customer pitch is compliance-driven, not F1-driven.

**P_deflated (benchmark-visible):** 0.05 (benchmarks do not measure this)
**P_deflated (compliance-visible):** 0.85 (audit trail IS the product for GDPR/EU AI Act customers)
**Note:** Do not conflate these two P values. The axis is high-value for customers; it is invisible to academic benchmarks.

---

### Axis 6: Online concept injection (continual learning without encoder retraining)

**What it is:** Substrate's sparse-KEY vocab injection (cycle 154 HP) adds new concept tokens to the KB without re-encoding or fine-tuning the sentence encoder. Strong encoders require re-training or PEFT to handle truly out-of-vocabulary concepts.

**Empirical state:** Cycle 154 sparse-KEY HP validated KB update latency and concept recall for injected concepts on the substrate's own encoder path. Not yet tested with bge-small as the upstream encoder.

**Lit-scan finding:** Continual learning literature (IKnow 2510.20377, Building adaptive knowledge bases 2025, Nature) confirms that knowledge injection without encoder retraining is a known gap. Current best practice either uses prompt-based injection (limited scope) or full continual pretraining (expensive). The substrate's KB-index-level injection is a distinct path closer to sparse adapter insertion but does not require gradient steps.

**Assessment:** EXISTS and meaningfully different from published baselines. But the feedback-drill-pretest-required memory rule applies: sparse-KEY must be validated on the production bge-small encoder path before claiming this as a win.

**P_theoretical:** 0.55 (mechanism is sound for truly OOV concepts)
**P_empirical:** 0.40 (cycle 154 was substrate's own encoder; bge-small OOV behavior is different)
**P_deflated:** 0.32
**HARD-PASS threshold:** New domain terms injected post-indexing retrieve at >= 70% of full-reindex recall
**HARD-FAIL threshold:** recall <= 40% -- concept injection does not generalize to bge-small's latent space

---

### Axis 7: Distributed reasoning across shards (CRDT bundle relay)

**What it is:** Substrate's CRDT merge + bundle relay gives 99.9% retrieval completeness at 50% node dropout. Strong encoders need external orchestration (e.g., LangChain routing) for cross-shard queries.

**Empirical state:** 99.9% dropout result validated on substrate's own path. Distributed bge-small RAG is typically orchestrated externally; substrate offers this natively.

**Lit-scan finding:** No standard RAG benchmark tests multi-shard retrieval at 50% dropout. The capability is real and validated but lives outside standard benchmark scope. Enterprise RAG (Pinecone, Weaviate) requires external federation layers that the substrate replaces.

**Assessment:** STRUCTURAL VALUE. Relevant for enterprise-scale customers with geographically distributed KBs. Not captured by academic benchmarks.

**P_deflated (benchmark-visible):** 0.05
**P_deflated (ops-visible):** 0.75

---

### Axis 8: Bitemporal point-in-time queries

**What it is:** Substrate records valid-time and transaction-time for every fact, enabling as-of queries (reconstruct the KB state at any past time). Strong encoders do not track temporality.

**Empirical state:** Architecture validated. No benchmark in HotpotQA / BEIR family tests historical reconstruction.

**Lit-scan finding:** Temporal QA benchmarks (TempQuestions, TimeQA) test time-sensitive factual reasoning but operate on static snapshots, not on dynamic KBs with temporal indexing. No published RAG benchmark tests bitemporal retrieval directly.

**Assessment:** STRUCTURAL VALUE ONLY for benchmarks. Real differentiator for legal/audit/financial use cases where reconstructing past system state is required.

**P_deflated (benchmark-visible):** 0.03
**P_deflated (compliance-visible):** 0.80

---

### Axis 9: Privacy-preserving retrieval (built-in rate-limit + audit)

**What it is:** Substrate has built-in rate limiting, access audit, and GDPR EDPB-3 right-to-erasure. Strong encoder RAG needs external privacy infrastructure.

**Empirical state:** Architecture validated (GDPR erasure design). Differential privacy at the retrieval layer requires additional work beyond current implementation.

**Lit-scan finding:** DP-RAG papers (arxiv 2412.04697, 2602.14374) show that differential privacy can be added to RAG without encoder retraining at epsilon=10, with modest QA accuracy tradeoff (match accuracy ~0.49-0.57 on Trivia at epsilon=10). The substrate's approach (audit + erasure + rate-limit) is complementary to DP but not the same mechanism. DP-RAG papers do not address right-to-erasure or Merkle audit trails. The two are composable.

**Assessment:** STRUCTURAL VALUE. Substrate does NOT currently have epsilon-DP guarantees (new feature). It has access audit + erasure, which addresses compliance but not information-theoretic privacy. Real differentiator for GDPR use cases.

**P_deflated (benchmark-visible):** 0.04
**P_deflated (compliance-visible):** 0.82

---

### Axis 10: Structured aggregate queries (SQL COUNT/SUM/predicate routing)

**What it is:** Substrate supports SQL-style COUNT, SUM, and predicate filters over the KB, extending retrieval to structured aggregates. Strong encoder RAG is point-retrieval only.

**Empirical state:** Predicate routing architecture exists. Not yet benchmarked on HybridQA or OTT-QA.

**Lit-scan finding:** KG-CQR (2508.20417) and KGMP (2025) add structured retrieval via KG extraction. HybridQA and OTT-QA are published benchmarks that measure hybrid structured-unstructured retrieval jointly. bge-small alone scores ~0 on COUNT/SUM aggregate queries in these benchmarks because point-retrieval cannot answer aggregates.

**Assessment:** EXISTS and is the one structural axis that maps to an existing published benchmark where bge-small alone scores zero. P_deflated is modest because predicate routing is not yet benchmarked, but the competitive gap (bge alone = 0 vs substrate = nonzero) is unusually clean.

**P_theoretical:** 0.50 (predicate routing algebra is sound)
**P_empirical:** 0.38 (not yet tested on HybridQA)
**P_deflated:** 0.32
**HARD-PASS threshold:** HybridQA predicate queries answered at >= 60% accuracy vs bge-small alone at ~0%
**HARD-FAIL threshold:** Implementation bugs in predicate routing cause <= 30% answer accuracy

---

## Stack ranking by P_actionable

| Rank | Axis | P_deflated | Pre-testable? | Benchmark-visible? |
|------|------|------------|----------------|-------------------|
| 1 | Adversarial robustness | 0.48 | Yes, 2h CPU | Yes (adversarial retrieval) |
| 2 | Noise robustness / BFT | 0.45 | Yes, 1h CPU | Yes (noisy retrieval settings) |
| 3 | Compositional precision reranking | 0.42 | Yes, 2h CPU | Yes (HotpotQA, MuSiQue) |
| 4 | Hallucination resistance | 0.40 | Bundled w/ Axis 1 | Yes (RAGAS, RAGLens) |
| 5 | Continual concept injection | 0.32 | Yes, 3h CPU | Partial (domain-shift benchmarks) |
| 6 | Structured aggregates | 0.32 | Yes, 4h CPU | Yes (HybridQA, OTT-QA) |
| 7 | Compliance: audit trail | 0.05/0.85 | N/A | No / Yes for compliance |
| 8 | Compliance: privacy (GDPR) | 0.04/0.82 | N/A | No / Yes for compliance |
| 9 | Distributed shards | 0.05/0.75 | N/A | No / Yes for ops |
| 10 | Bitemporal queries | 0.03/0.80 | N/A | No / Yes for legal |

---

## Falsifiable predictions: HARD-PASS and HARD-FAIL

**Adversarial robustness:**
- HARD-PASS: substrate confidence filter reduces adversarial rank injection by >= 30% in pre-test
- HARD-FAIL: reduction <= 10% -- this axis closes

**Noise robustness:**
- HARD-PASS: H=2 BFT gives >= 5% recall lift at noise std=0.20 over bge-small H=1
- HARD-FAIL: lift <= 1% -- BFT voting adds no value when bge embeddings are stable

**Compositional precision:**
- HARD-PASS: precision@3 improves >= 15% on 2-hop questions vs bge-small alone
- HARD-FAIL: precision@3 improves <= 5% -- structured reranking adds no signal beyond bge similarity

**Continual concept injection:**
- HARD-PASS: injected OOV concepts retrieve at >= 70% of full-reindex recall
- HARD-FAIL: recall <= 40% -- injection does not generalize to bge-small latent space

**Structured aggregates:**
- HARD-PASS: HybridQA predicate queries at >= 60% accuracy vs bge-small ~0%
- HARD-FAIL: predicate routing bugs cause <= 30% accuracy

---

## Cross-thread synthesis

- Retrieval encoder selection 3x drill (2026-06-07): confirmed bge-small is the v1 encoder and that HotpotQA 2-hop gap is a multi-hop reasoning problem, not a coverage problem. This drill's Axis 3 (compositional reranking) is the substrate's direct path to closing that gap without replacing bge-small.

- Pattern B compositional storage 3x drill (2026-06-07): confirmed VSA algebra works; SRL is the go/no-go gate. Axis 3 here inherits that risk. The 2h CPU pre-test for Axis 3 is the same SRL accuracy test already flagged in that drill. These two pre-tests can be run together.

- Pattern B compliance/distributed inheritance drill (2026-06-07): confirmed all 15 compliance features transfer. Axes 5-9 here (audit, privacy, distributed, bitemporal, aggregates) are exactly those features. This current drill adds the honest quantification: they are real but benchmark-invisible.

- Cycle 145 KF-1 adversarial result: AUC 0.96-0.97 on 6 attack types on substrate's own path. Axis 1 proposes the direct head-to-head test of that defense applied to bge-small outputs. The algebra is encoder-agnostic so transfer is theoretically clean.

- Cycle 154 sparse-KEY HP: supports Axis 6 conceptually. But the drill-pretest-required memory rule applies before this axis can be claimed.

---

## Honest assessment: measurable vs structural value-add

**The retrieval K-hop pitch specifically:**
Based on cycles 156-157, K-hop hurts strong encoders (-2.7% on bge-small, similar on bge-large). K-hop should be disabled by default for well-indexed dense KBs and reserved for scenarios with weak encoders OR sparse KB graph structure where chain coverage fills genuine gaps that dense retrieval misses.

**Benchmark-measurable axes (can show recall/precision numbers):**
Axes 1-4 (adversarial robustness, noise robustness, compositional precision, hallucination resistance) and Axis 10 (structured aggregates). These 5 axes can produce head-to-head numbers against bge-small alone on published benchmarks. P_deflated range 0.32-0.48. None have been pre-tested yet; all require a 1-4h CPU pre-test before claiming benchmark wins.

**Structural-only axes (architecture wins, not benchmark wins):**
Axes 5-9 (audit trail, concept injection partial, distributed shards, bitemporal, privacy/GDPR). These are real and valuable for regulated industries. For finance, healthcare, legal, EU compliance customers they ARE the primary pitch. They will not appear in BEIR, HotpotQA, NDCG, or recall@K leaderboards. Do not try to force these into a retrieval benchmark comparison; they live in a different product category.

**Summary of the customer pitch revision needed:**

The single-track pitch ("substrate lifts retrieval recall") is only defensible for weak encoders. For bge-small and above, the pitch must split into two tracks:

Track A (robustness, benchmark-testable): adversarial defense, noise immunity, compositional precision, hallucination resistance. Requires pre-testing Axes 1-3 first. If pre-tests pass, these become headline benchmark claims.

Track B (compliance, not benchmark-testable but legally required): Merkle audit trail, GDPR erasure, bitemporal as-of queries, distributed fault-tolerant retrieval. For regulated industries, these are requirements, not optional features. EU AI Act Article 12 August 2026 creates a hard deadline that pulls this cluster.

---

## Recommended cheap pre-tests (top 3)

**Pre-test 1: Adversarial robustness (Axes 1 + 4 bundled)**
- Time: 2h CPU
- Setup: Index 10K passages from a public QA KB with bge-small. Inject 200 adversarial passages (HotFlip corpus poisoning attack type). Run retrieval with and without substrate confidence filter T=0.5.
- Measure: Adversarial rank injection rate (fraction of adversarial passages in top-10), and hallucination AUC on a 100-question probe.
- Pre-reg: HARD-PASS if injection reduction >= 30%, HARD-FAIL if <= 10%.

**Pre-test 2: Noise robustness (Axis 2)**
- Time: 1h CPU
- Setup: Index 10K bge-small embeddings. Add Gaussian noise std=0.20 to 20% of stored vectors. Run H=1 vs H=2 retrieval on 500 queries from a public QA set.
- Measure: recall@10 gap between H=1 and H=2.
- Pre-reg: HARD-PASS if H=2 gain >= 5%, HARD-FAIL if <= 1%.

**Pre-test 3: Compositional precision (Axis 3)**
- Time: 2h CPU (can be combined with Pattern B SRL pre-test)
- Setup: Take HotpotQA 100-question bridge subset. Use bge-small to retrieve top-10 per query. Apply substrate Pattern B compositional reranker to select top-3. Compare to bge-small top-3 on precision@3.
- Measure: precision@3 improvement.
- Pre-reg: HARD-PASS if improvement >= 15%, HARD-FAIL if <= 5%.
- Note: This pre-test is shared with the Pattern B SRL pre-test flagged in the earlier drill. If SRL accuracy is >= 80%, run Axis 3 as an extension (30 min additional).

---

## Substrate-product implications

1. K-hop is a conditional feature. Introduce a heuristic gate: enable K-hop only when encoder quality is below a threshold (estimated recall@10 < 0.25 on a validation probe). At bge-small quality, K-hop adds noise and should be off by default.

2. The three benchmark-testable axes (Axes 1-3) should each have a 2h CPU pre-test before engineering investment. P_deflated range 0.42-0.48 makes these the strongest near-term bets for demonstrating measurable value-add over bge-small alone.

3. The compliance cluster (Axes 5, 8, 9) does not need a benchmark win. It needs a compliance certification path and a clear EU AI Act Article 12 alignment story. These are separate product tracks.

4. Structured aggregates (Axis 10) is the one structural feature that maps to an existing benchmark (HybridQA/OTT-QA) where bge-small alone scores ~0. This is a clean gap. If engineering capacity is available after the top-3 pre-tests, Axis 10 should be queued next.

---

## Citations (verified from lit-scan)

1. arxiv 2407.06992 -- "Robust Neural Information Retrieval: An Adversarial and Out-of-distribution Perspective" (survey 2024)
2. arxiv 2504.17884 -- "Unsupervised Corpus Poisoning Attacks in Continuous Space for Dense Retrieval" (2025)
3. arxiv 2308.09861 -- "Black-box Adversarial Attacks against Dense Retrieval Models: A Multi-view Contrastive Learning Method" (2023)
4. arxiv 2507.06956 -- "Investigating the Robustness of Retrieval-Augmented Generation at the Query Level" (2025)
5. arxiv 2506.00054 -- "Retrieval-Augmented Generation: A Comprehensive Survey of Architectures, Enhancements, and Robustness Frontiers" (2025)
6. arxiv 2412.04697 -- "Privacy-Preserving Retrieval-Augmented Generation with Differential Privacy" (2024)
7. arxiv 2602.14374 -- "Differentially Private Retrieval-Augmented Generation" (2026)
8. arxiv 2601.03979 -- "SoK: Privacy Risks and Mitigations in Retrieval-Augmented Generation Systems" (2026)
9. arxiv 2506.08074 -- "Hierarchical Lexical Graph for Enhanced Multi-Hop Retrieval" (2025)
10. arxiv 2510.14278 -- "PRISM: Agentic Retrieval with LLMs for Multi-Hop Question Answering" (2025)
11. arxiv 2508.20417 -- "KG-CQR: Leveraging Structured Relation Representations in Knowledge Graphs for Contextual Query Retrieval" (2025)
12. arxiv 2601.05866 -- "FACTUM: Mechanistic Detection of Citation Hallucination in Long-Form RAG" (2026)
13. arxiv 2506.06240 -- "Bridging External and Parametric Knowledge: Mitigating Hallucination" (2025)
14. arxiv 2510.20377 -- "IKnow: Instruction-Knowledge-Aware Continual Pretraining for Effective Domain Adaptation" (2025)
15. MDPI Sensors 2025 -- "SelectVote Byzantine Fault Tolerance for Evidence Custody" (2025)

Verified count: 15

---

*Note path: notes/research_drill_substrate_value_add_strong_encoders_3x_2026-06-07.md*
