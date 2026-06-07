# Research Drill: Substrate Compositional Filtering -- Regime Analysis (2x depth)
## Date: 2026-06-07
## Topic: When does substrate compositional filtering beat brute-context top-K?

---

## HEADLINE

Substrate compositional filtering loses to brute-context top-10 at 1.5B LLM scale because small LMs extract reliably from broad recall@10=0.74 context; the information discarded by pre-filtering is not recoverable at inference. However, three regimes exist where filtering wins: (1) context-window-constrained large-KB deployments, (2) adversarial/noisy retrieval pools, and (3) structured multi-hop queries requiring graph-verifiable provenance. The crossover to filtering-wins depends on KB scale more than LLM scale above ~7B parameters.

---

## Prediction Validity Block

Pre-registered before synthesis:

HARD-PASS: At least 3 of 7 regimes show mechanistically defensible filtering advantage with lit-cited support and quantified crossover condition.
HARD-FAIL: Filtering advantage is theoretical-only with no empirical benchmark precedent, OR all 7 regimes favor brute-context unconditionally.

Calibration: This is a 2x drill on existing empirical findings (cycle 161 HF verdict). P_deflated splits below.

---

## Part 1: Seven-Regime Evaluation

### Regime 1: Long-Context Bottlenecked (KB too large for window)

Mechanism: When retrieval returns K candidates that collectively exceed the LLM context window, the system must truncate. Truncation is arbitrary. Pre-filtering via compositional structure selects K_filtered < K best candidates instead of truncating blindly.

Evidence: "Context Length Alone Hurts LLM Performance Despite Perfect Retrieval" (arxiv 2510.05381) shows 13.9-85% degradation as input length increases even with perfect retrieval and no distractors. This is not about noise -- it is pure attention dilution from length. The lost-in-the-middle phenomenon (Liu et al. 2023) shows LLMs attend best to beginning and end of context; middle tokens drop 30-50% in extraction accuracy on multi-document QA.

Crossover condition: When top-K retrieved passages exceed roughly 3,000-5,000 tokens total (2K context models) or 8,000-16,000 tokens (8K context models). At K=10 with 150-token passages, total is ~1,500 tokens -- below the cliff. At K=50 with 300-token passages, total is ~15,000 tokens -- above the cliff. Substrate filtering wins when K is large, not when K=10.

Verdict for current setup (K=10, 1.5B, short passages): LOSE. Filtering loses because K=10 is well within 1.5B context capacity and brute-context recall wins. Substrate wins when K >= 30 or passage length >= 500 tokens.

P_theoretical (filtering wins at large K): 0.72 (deflated from 0.85, -0.13 calibration penalty)
P_empirical (tested at current K=10): 0.08 -- confirmed loss, consistent with theory

---

### Regime 2: Latency-Bottlenecked (token budget matters)

Mechanism: LLM inference cost scales with input token count. Passing 10 documents costs 10x tokens vs 1 document. When SLA requires sub-100ms LLM inference or cost-per-query is tight, filtering to 1-2 candidates reduces cost dramatically.

Evidence: Databricks long-context RAG blog and Redis RAG-vs-large-context post both document that passing full corpus without filtering is inferior to selective RAG on price and latency metrics. The computational cost of inference grows roughly linearly with context length for transformer attention (quadratically in the extreme).

Crossover condition: Deployment where LLM per-token cost > retrieval filtering cost. This is system-architecture dependent, not a fixed LLM scale. At 1.5B local inference with no API cost, the crossover is higher than at GPT-4o API pricing.

Verdict: CONDITIONAL WIN. Filtering wins on latency/cost in API-billing environments or edge deployments. Not about accuracy -- about throughput.

P_theoretical: 0.68 (deflated from 0.80, -0.12 calibration)
P_empirical: 0.50 -- latency benefit is real but not yet tested in this substrate

---

### Regime 3: High-Precision Attribution Required

Mechanism: Some tasks require exact provenance: "cite the specific document that supports this claim." Brute-context LLMs hallucinate or blend sources. Compositional substrate selection provides a ranked source list with graph-verifiable provenance. The answer is tied to a specific node pair, not inferred from mixed context.

Evidence: Graph-RAG literature (HopRAG arxiv 2502.12442, StepChain GraphRAG 2510.02827) shows that subgraph-structured context achieves twice the precision of vector-only retrieval for multi-hop facts. The substrate's Pattern B structure explicitly encodes which source nodes contributed to which answer candidate, enabling auditability.

Crossover condition: Tasks where hallucination risk or source attribution matters more than recall. Regulated domains: healthcare (cite the study), legal (cite the case), compliance (cite the policy). General consumer QA does not trigger this.

Verdict: WIN in regulated contexts. Not an accuracy win -- a trust/auditability win. Different axis from F1.

P_theoretical: 0.75 (deflated from 0.88, -0.13 calibration)
P_empirical: Not yet tested; requires audit-trail evaluation metric

---

### Regime 4: Adversarial / Misleading Distractors in Retrieval Pool

Mechanism: When the top-K retrieved documents contain adversarially crafted or semantically similar but factually incorrect items, brute-context LLMs extract wrong answers. Magic Mushroom benchmark (arxiv 2506.03901) and RGB benchmark define 4 noise types; RAAT adversarial training shows F1 improvements of 20-30% from noise-robust approaches.

Evidence: Smaller LLMs (the 1.5B regime) are MORE vulnerable to distractors than larger LLMs. The model-size filtering analysis directly states: "noisy information negatively affects smaller models more." This creates a specific favorable condition: at 1.5B scale, adversarial distractors in top-10 harm brute-context more than at 7B scale.

Crossover condition: When recall@10 contains >= 2-3 adversarially similar but incorrect items (semantically close, factually wrong). In the north-star benchmark (recall@10=0.74), ~2.6 of 10 items are non-relevant but are they adversarial? If they are random irrelevants, small LMs mostly ignore them. If they are confounders, filtering wins.

Verdict: WIN at 1.5B if distractor fraction is high. The north-star setup uses recall@10=0.74 which implies ~2.6 non-relevant items -- but these are likely random non-relevant, not adversarial confounders. In adversarial-KB scenarios, filtering wins more strongly at small LM scale.

P_theoretical (adversarial KB): 0.62 (deflated from 0.78, -0.16 calibration)
P_empirical (current benign setup): 0.12 -- consistent with current loss

---

### Regime 5: Structured / Compositional Queries

Mechanism: Natural-language questions that decompose into subqueries -- "find all events where subject=X AND property=Y" -- are naturally served by graph traversal rather than dense retrieval. Substrate Pattern B (compositional structure) is designed for exactly this: enumerate 2-hop paths satisfying both head and tail constraints.

Evidence: UniKGQA (arxiv 2212.00959), HopRAG (2502.12442), and StepChain GraphRAG (2510.02827) all show structured graph retrieval outperforming dense retrieval on compositional multi-hop questions. Vector+graph RAG achieves "more than twice the precision and recall of systems based solely on vector RAG" for structured queries. Graph-walk context compression reduces tokens by ~60% while improving relevant-fact density.

Crossover condition: Query complexity. Single-hop factoid ("who is X?") -- dense retrieval wins. Two-hop compositional ("what did X do at Y?") -- graph structured retrieval competitive. Three-hop or more -- graph structured retrieval wins clearly, dense retrieval degrades rapidly.

Verdict: WIN for 2+ hop compositional queries. This is the clearest advantage case. The substrate's Pattern B is architecturally aligned with 2-hop structured retrieval. The failure in cycle 161 was using Pattern B for SELECTION among candidates, not for GRAPH TRAVERSAL to find candidates. The use case was wrong, not the mechanism.

P_theoretical: 0.78 (deflated from 0.90, -0.12 calibration)
P_empirical: Not yet tested on purely compositional KB queries

---

### Regime 6: Multi-Step Reasoning Chains (step-verified outputs)

Mechanism: Tasks where each reasoning step's output feeds the next step, and each step requires verification against the KB. Example: "Given X's age, compute Y, then find all entities with property > Y." Brute-context LLMs can hallucinate intermediate steps. Substrate compositional verification of each step prevents error propagation.

Evidence: PRISM agentic retrieval (arxiv 2510.14278) and FltLM (arxiv 2410.06886) both show that iterative filtering with step-verification outperforms single-pass large-context for multi-step reasoning chains. The benefit grows with chain length.

Crossover condition: Chain depth >= 3 steps. For 1-2 step chains (standard 2-hop QA), LLM can hold context. For 3+ step chains with per-step KB lookups, structured verification prevents accumulating errors.

Verdict: WIN at chain depth >= 3. Not relevant to the current north-star QA benchmark (single-turn QA). Relevant for agentic workflows with iterative KB access.

P_theoretical: 0.65 (deflated from 0.80, -0.15 calibration)
P_empirical: Not yet tested

---

### Regime 7: Privacy / Selective Context Exposure

Mechanism: When the KB contains sensitive records and the system must not expose irrelevant records to the LLM (which may be a hosted API), filtering to only relevant candidates reduces the privacy attack surface. Differential privacy RAG (arxiv 2412.04697) and entity-perturbation methods show that selective retrieval is a core privacy-preserving strategy.

Evidence: Privacy risks are documented specifically in healthcare, legal, and financial domains. The strategy of limiting context to only what is needed is structurally equivalent to substrate compositional filtering -- pass fewer but more relevant documents.

Crossover condition: Regulated deployments (HIPAA, GDPR, attorney-client privilege) where every token passed to an LLM API is a potential disclosure event.

Verdict: WIN on privacy surface reduction. Not an accuracy advantage -- a compliance advantage. Different axis.

P_theoretical: 0.70 (deflated from 0.82, -0.12 calibration)
P_empirical: No empirical test exists yet; purely compliance-architectural

---

## Part 2: Crossover Analysis

### LLM Scale Crossover

The evidence from the search results gives a nuanced picture:

At 1.5B: strong sensitivity to both length and noise. Brute-context wins when recall@10 is high (0.74) and distractors are benign. Filtering wins when distractors are adversarial.

At 7B: noise robustness increases substantially. The WebQA dataset shows 3.05% accuracy gap between 7B and 72B with RAG vs 28.87% without RAG. RAG has larger relative benefit at smaller scale.

At 7B+: brute-context is more robust, but long-context degradation still applies (13.9-85% by context length). Filtering still wins on latency/cost.

Key finding: LLM scale crossover is NOT the dominant axis. The dominant axis is KB scale (how large K needs to be) and query structure (compositional vs factoid). Scale from 1.5B to 7B does not flip the filtering advantage for structured/compositional queries -- those win regardless of LLM size because the bottleneck is retrieval structure, not extraction capacity.

Null result on "does 7B benefit from substrate composition where 1.5B does not?": The answer is no -- both benefit from structured filtering for structured queries, and neither needs it for factoid QA with small K and benign recall pool.

### KB Scale Crossover

This is the more important axis:

- At K=10, 1K-fact KB: brute-context wins (recall@10=0.74 is good enough, context fits)
- At K=30, 10K-fact KB: context pressure begins; filtering value increases
- At K=50+, 100K-fact KB: precision@K degrades; without filtering, LLM gets noisy context; graph-structured filtering wins clearly
- At 1M+ facts: brute retrieval recall@10 degrades significantly; structured graph retrieval maintains quality by constraining the search

The crossover is roughly at K=25-30 retrieved candidates or 100K+ KB facts. Below these thresholds, brute-context dominates. Above them, compositional filtering adds value.

---

## Part 3: Stack Ranking (Best Regimes for Substrate Compositional Filtering)

Tier 1 (strongest case, multiple evidence streams):

1. Structured/Compositional Queries (Regime 5) -- This is mechanistically exact alignment. The substrate's Pattern B is a 2-hop graph traversal. Using it for selection among dense-retrieved candidates (as in cycle 161) is the wrong use. Using it for graph-structured retrieval of 2-hop fact paths is the right use. Lit precedent: HopRAG, UniKGQA, GraphRAG show 2x precision for these queries. P_theoretical=0.78.

2. Long-Context Bottlenecked / Large KB (Regime 1) -- Filtering wins when K is large. The current failure (K=10) is below the crossover. A test at K=50 with a 100K-fact KB would likely flip the result. P_theoretical=0.72, backed by arxiv 2510.05381 (context length alone hurts 13.9-85%).

Tier 2 (real but narrower advantage):

3. Adversarial Distractors (Regime 4) -- Specifically wins at 1.5B scale when distractor fraction is high. The current north-star setup likely does not trigger this. Adversarial-KB is a real deployment scenario (competitor injection, spam, misinformation). P_theoretical=0.62.

4. High-Precision Attribution / Auditability (Regime 3) -- Not an F1 win but a trust/compliance win. Regulated industries (healthcare, legal) care about source traceability more than aggregate F1. P_theoretical=0.75 but on a different metric.

Tier 3 (real but conditional):

5. Latency/Cost (Regime 2) -- Wins on API-billing deployments, irrelevant for local inference.
6. Multi-Step Chains (Regime 6) -- Wins at chain depth >= 3, not in single-turn QA.
7. Privacy (Regime 7) -- Compliance win, not accuracy win. Hard to test empirically.

---

## Part 4: Cheap Pre-Tests for Top 2 Regimes

### Pre-Test A: Large-K Context Pressure (Regime 1)

Test design (generic -- no substrate-specific terms):

Run the same QA benchmark with K varied: K=5, 10, 20, 50.
- Metric: F1 at each K with brute-context vs filtered-to-K/5.
- Hypothesis: Brute-context F1 peaks at some K* then degrades. Filtering maintains F1 above K*.
- Expected K* crossover: 20-30 based on context-length-hurts literature.
- Wall time: 2-3 hours on existing local runner with existing model.
- Cost: $0 (local GPU).

Per drill-pretest-required rule: This requires a 1-2 hour production encoder pre-test before engineering authorization. The pre-test is: run the K=50 brute-context condition first on the existing benchmark to confirm F1 degradation occurs. If F1 drops by >= 0.05 relative to K=10, the crossover exists and engineering authorization is warranted.

P_theoretical x P_empirical:
- P_theoretical (crossover exists at K=30-50): 0.72
- P_empirical (will we see it in this specific LM): 0.55 (requires pre-test to validate; deflated per drill-pretest-required)

HARD-PASS: F1(K=50, brute) < F1(K=10, brute) - 0.04 AND F1(K=50, filtered) > F1(K=50, brute) + 0.03
HARD-FAIL: F1(K=50, brute) >= F1(K=10, brute) with delta < 0.01 (no degradation = crossover does not exist in this deployment)

---

### Pre-Test B: Compositional Query Subtype (Regime 5)

Test design:

Carve out a subset of the existing benchmark questions that are naturally compositional (require 2 entities + 1 relationship). Reframe retrieval as graph traversal (find K candidates via 2-hop expansion from query entities) vs dense retrieval (top-K by embedding similarity).
- Metric: F1 on compositional subset only vs factoid subset.
- Hypothesis: Graph-structured retrieval wins on compositional subset; dense wins on factoid.
- Wall time: 3-4 hours including subset annotation.
- Cost: $0 (local).

Per drill-pretest-required rule: Pre-test is annotation of compositional vs factoid question split in the existing QA dataset. If <15% of questions are compositional, the effect size will be undetectable (insufficient power). Check compositional fraction first.

P_theoretical x P_empirical:
- P_theoretical (graph wins on compositional subset): 0.78
- P_empirical (enough compositional questions exist in benchmark): 0.45 (uncertain; depends on benchmark composition; deflated per calibration rule)

HARD-PASS: F1(graph, compositional) > F1(dense, compositional) + 0.05 AND compositional subset >= 20 questions
HARD-FAIL: Compositional subset < 10 questions (insufficient power) OR F1(graph, compositional) <= F1(dense, compositional)

---

## Part 5: Cross-Thread Synthesis

Cycle 156-157 (K-hop encoder degradation): Same information-loss pattern. Substrate graph structure helps strong encoders find paths but damages extraction by reducing context diversity. Both cycles confirm the substrate's structural role is PROVIDING PATH STRUCTURE for traversal, not FILTERING among post-retrieval candidates.

Cycle 161 (bge_compositional_verify HF): The specific failure mode was using Pattern B for selection FROM dense-retrieved top-10. This is categorically a wrong-use-case match: the substrate's strength is graph-structured candidate generation (2-hop path traversal), not semantic re-ranking of dense retrievals. The verdict "information loss > precision gain" is correct but understates the mechanism: the substrate was being asked to do re-ranking, which is not its architecture's strength.

North-star +0.35 F1: This win was achieved by the substrate providing CONTEXT (the 2-hop retrieved documents), not by filtering the context. This is the correct use case alignment: substrate = context expansion; LLM = context extraction. The drift toward using substrate for post-retrieval filtering is moving away from what produced the north-star win.

Synthesis: The correct substrate role model is: use Pattern B to EXPAND retrieval coverage (graph traversal to find 2-hop candidate pairs) and pass ALL found candidates to the LLM. Do not use Pattern B to SELECT among candidates already found by dense retrieval. The former is a structural advantage; the latter fights the LLM's extraction ability.

---

## Part 6: Substrate-Product Implications

General consumer QA product positioning: Substrate adds value through recall expansion (finding facts that dense retrieval misses via 2-hop paths), NOT through post-retrieval filtering. Product story: "we find more relevant context" not "we filter better context."

Regulated-industry product positioning: Substrate adds value through auditability (provenance traces from answer back to specific graph nodes), privacy surface reduction (fewer irrelevant documents exposed), and structured multi-hop query support. Product story: "we trace every answer to its source" -- this is a different axis from F1.

Enterprise/large-KB positioning: Substrate adds value when KB grows to 100K+ facts where dense retrieval recall@K degrades and K must be large. At that scale, substrate graph structure constrains search to relevant subgraphs rather than flooding context with semantically similar but topically irrelevant items.

What substrate composition is NOT for: Re-ranking dense retrieval candidates at small K, single-hop factoid QA, and general consumer question answering with benign retrieval pools. Cycle 161 tested exactly this non-use case and got the expected failure.

Key recommendation: Engineering energy on substrate composition should focus on graph-traversal retrieval (generating candidates via 2-hop paths) rather than post-retrieval selection. These are different algorithms with different performance profiles. The north-star result used the former. Cycle 161 tested the latter and confirmed the loss.

---

## Part 7: Honest Assessment -- Commercial Positioning

Substrate compositional filtering is NOT a general-purpose retrieval improvement. It is a targeted capability that wins in specific deployment contexts:

1. Regulated industries requiring auditability (healthcare, legal, compliance)
2. Large-KB enterprise deployments where K must be large (100K+ facts, K=30+)
3. Natively compositional query workloads (structured multi-hop questions)
4. Adversarial environments where the retrieval pool is contaminated

For the north-star benchmark (memory-augmented general QA, K=10, benign recall pool), substrate composition does not add filtering value. The product win in that benchmark comes from graph-structured RECALL EXPANSION (finding 2-hop facts that dense retrieval misses), not from post-retrieval filtering.

This is an important distinction for positioning: the substrate's value is in the GRAPH STRUCTURE for retrieval, not in the post-retrieval intelligence. The LLM handles extraction from broad context better than the substrate handles selection. Lean into substrate-as-retrieval-structure, not substrate-as-ranker.

Customer segments that benefit most from substrate FILTERING (not just recall):
- Healthcare informatics: multi-hop clinical evidence retrieval with attribution
- Legal document platforms: structured query support + provenance for citations
- Enterprise knowledge management with large KB (10K+ structured facts)
- Compliance/audit systems: traceable reasoning chains

Customer segments that do NOT benefit from substrate FILTERING (but do benefit from substrate RECALL):
- General consumer QA
- Standard RAG chatbots with small KB
- Single-hop factoid lookup

---

## Cheap Decisive Test (top-level)

Run existing QA benchmark at K=50 (brute-context) and check if F1 drops vs K=10. If yes, crossover exists and substrate filtering pre-test is warranted. If no, focus engineering on structured-query subtype testing instead.

Wall time: 2 hours. Cost: $0.

---

## Falsifiable Predictions

HARD-PASS (confirms filtering regime):
- F1(K=50, brute) < F1(K=10, brute) - 0.04 on existing QA benchmark
- OR: F1(graph-traversal, compositional subset) > F1(dense, same subset) + 0.05 with N>=20 compositional questions

HARD-FAIL (confirms brute-context dominance in current setup):
- F1(K=50, brute) >= F1(K=10, brute) - 0.01 (no K degradation)
- AND F1(graph-traversal, compositional subset) <= F1(dense, compositional subset)

---

## Citations (verified, from search results)

1. arxiv 2510.05381 -- Context Length Alone Hurts LLM Performance Despite Perfect Retrieval (13.9-85% degradation with length)
2. Liu et al. 2023 -- Lost in the Middle: How Language Models Use Long Contexts
3. arxiv 2506.03901 -- Magic Mushroom: Customizable Benchmark for Retrieval Noise Erosion in RAG
4. arxiv 2412.04697 -- Privacy-Preserving RAG with Differential Privacy
5. arxiv 2502.12442 -- HopRAG: Multi-Hop Reasoning for Logic-Aware RAG
6. arxiv 2212.00959 -- UniKGQA: Multi-hop KG QA
7. arxiv 2510.02827 -- StepChain GraphRAG multi-hop KG reasoning
8. arxiv 2410.06886 -- FltLM: Long-Context LLM with Selective Filtering
9. arxiv 2510.14278 -- PRISM: Agentic Retrieval with LLMs for Multi-Hop QA
10. Databricks Blog -- Long Context RAG Performance of LLMs
11. Redis Blog -- RAG vs Large Context Window AI Apps
12. arxiv 2405.20978 -- RAAT: Adversarial Training for RAG Noise Robustness (20-30% F1 gain)
13. arxiv 2601.11564 -- Context Discipline and Performance Correlation
14. Singlestore Blog -- How GraphRAG Improves Multi-Hop Reasoning (2x precision vs vector-only)

Verified citation count: 14

---

## P_deflated Summary

| Regime | P_theoretical | P_empirical | Status |
|---|---|---|---|
| 1. Large-K bottleneck | 0.72 | 0.08 (tested, lost) | Pre-test K=50 needed |
| 2. Latency/cost | 0.68 | 0.50 | Architecture-dependent |
| 3. Attribution/auditability | 0.75 | untested | Regulated domain play |
| 4. Adversarial distractors | 0.62 | 0.12 (benign pool) | Adversarial-KB test needed |
| 5. Compositional queries | 0.78 | untested | Best candidate for win |
| 6. Multi-step chains | 0.65 | untested | Agentic workflow |
| 7. Privacy | 0.70 | untested | Compliance axis only |

All P values deflated 0.12-0.16 per calibration penalty rule. Novel-synthesis cap 0.50 not triggered (lit precedent exists for all claims).

---

## Next-Drill Candidate

Graph-structured retrieval for compositional query subsets (Regime 5). The 2-hop graph traversal as the retrieval mechanism (not as post-retrieval selector) is the most mechanistically aligned and has the strongest lit precedent. A pre-test carving compositional vs factoid question subsets from the existing benchmark would take 3-4 hours and directly validate or falsify the core regime prediction.
