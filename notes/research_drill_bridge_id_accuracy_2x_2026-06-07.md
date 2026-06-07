# Research Drill: Bridge-ID Accuracy Improvement Strategies (2x Operational Drill)
**Date:** 2026-06-07
**Filed by:** research sub-agent (2x user-mandated drill; focus: bridge-ID bottleneck)
**Importance:** CRITICAL -- multi-hop revival; separate bottleneck from bridge coverage
**Prior drill:** notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md

---

## HEADLINE

At 1.5B LLM with regex NER, bridge-ID accuracy is approximately 60-65%. The self-improving routing architecture closes the BRIDGE COVERAGE gap at equilibrium (90%+ at Q=100K) but does NOT close the BRIDGE-ID accuracy gap -- these are orthogonal failure modes. Closing bridge-ID from 60% to 75%+ requires either (a) a dedicated LoRA-fine-tuned bridge classifier (highest lift, ~70-80% theoretical, 6-10 eng-days), (b) multi-stage cascade NER+substrate-frequency+LLM-verify (highest near-term lift with no training, ~70-75% theoretical, 3-5 eng-days), or (c) Pattern-B algebraic bridge generation (bypasses NER entirely, ~80%+ at warm substrate, 0 training cost, but requires bridge coverage to be pre-seeded). The three-way multi-hop accuracy formula P(2hop) = P(bridge_id) * P(coverage) * P(unbind_given_hit) shows that at bridge_id=0.60 and coverage=0.90, the ceiling is 0.54. Pushing bridge_id to 0.78 while maintaining coverage=0.90 reaches 0.70 exactly -- the stated target. This gap is closeable. P_theoretical = 0.62, P_empirical = 0.35 (calibration penalty applied; -0.20 from raw estimate; novel-synthesis cap at 0.50 for options requiring training).

---

## Cheap Decisive Test

**2-hour pre-test: spaCy lg vs DistilBERT-NER vs 1.5B LLM-as-NER on 200 HotpotQA bridge questions.**

Procedure:
1. Take 200 HotpotQA bridge questions (downloaded from the HotpotQA dev set; bridge questions are labeled as type="bridge").
2. Extract the ground-truth bridge entity from the answer + supporting facts.
3. Run three extractors on the question text: (a) spaCy en_core_web_lg NER, (b) dslim/bert-base-NER from HuggingFace, (c) the existing 1.5B LLM with the current prompt.
4. Score each extractor: bridge_id_correct = 1 if the ground-truth bridge entity (or a string-normalized match) appears in the top-3 candidates returned.
5. Compute accuracy for all three.

Cost: ~30 min download + ~1.5 hr runtime on CPU. No GPU needed. No training.

HARD-PASS criterion: DistilBERT-NER or spaCy lg achieves >= 72% bridge-ID accuracy on these 200 questions.
HARD-FAIL criterion: All three extractors below 65% accuracy, OR DistilBERT-NER is no better than spaCy lg (indicates the task requires understanding beyond token classification; ruling in favor of Option 8 training path).

This pre-test answers: "Is the bottleneck solvable with a drop-in NER upgrade, or does it require training a dedicated bridge-ID head?" The answer directly sequences v1.1 engineering.

---

## Falsifiable Predictions

### HARD-PASS thresholds (bridge-ID accuracy improvement)
- P1: DistilBERT-NER achieves >= 72% on HotpotQA bridge-200 pre-test (PASS criterion for Option 2 fast-path).
- P2: Multi-stage NER+frequency+verify cascade achieves >= 74% bridge-ID on bridge-200 (PASS criterion for Option 2 composition).
- P3: LoRA-fine-tuned bridge classifier (Option 8) achieves >= 78% bridge-ID on HotpotQA dev held-out 500 questions.
- P4: Pattern-B algebraic bridge generation (Option 5) achieves >= 80% bridge-ID at warm substrate (bridge coverage >= 85%).
- P5: At bridge_id >= 0.78 and coverage >= 0.88, the compound multi-hop accuracy P(2hop) >= 0.62.

### HARD-FAIL thresholds
- F1: DistilBERT-NER on bridge-200 pre-test is below 65% -- indicates the bottleneck is not a NER quality problem but a question understanding / decomposition problem; NER upgrades are the wrong investment.
- F2: Multi-stage cascade below 68% -- indicates the bridge entity is not surfaced clearly enough in the question text for any extractor; substrate-side option (Pattern-B algebraic generation, Option 5) becomes the primary path.
- F3: At bridge_id = 0.78 and coverage = 0.88, P(2hop) < 0.55 -- indicates a third failure mode not in the formula (wrong unbind step, error propagation in multi-hop chain).
- F4: Substrate-augmented bridge prediction (Option 3) below 60% at Q=10K warm -- indicates the bridge vocabulary is too sparse for frequency-based lookup to help at this scale.

---

## 12 Strategies: Stack-Ranked by P_actionable

The stack-rank uses: P_lift (probability the option actually raises bridge-ID by >= 10pp) * P_cost_ok (probability the eng cost is feasible for v1.1) - calibration penalty (0.15-0.20).

### Rank 1 -- Option 8: Bridge Annotation LoRA Fine-Tuning
**What it is:** Train a dedicated bridge-entity extraction head on top of a small LLM (1.5B or smaller) using HotpotQA's labeled bridge entities. LoRA keeps the parameter count low; supervised signal is strong because HotpotQA provides bridge entity ground truth for ~90K training examples.

**Mechanism:** Add a token-classification head on top of the LLM's last hidden state. Fine-tune with LoRA on span-extraction objective: given question text, predict BIO tags for bridge entity spans. The bridge entity is defined as the entity that appears in the first-hop supporting fact title and is also mentioned in the question or second-hop.

**Theoretical lift:** LoRA + supervised NER on domain-matched data (HotpotQA) produces F1 >= 0.89 in analogous settings (LLM-NER paper: Llama-3-8B LoRA micro-F1 = 0.894; DistilBERT-NER on CoNLL = 0.916). For a bridge-specific fine-tune at 1.5B, a conservative estimate is 78-83% accuracy (deflated from raw 88% by 0.10 for domain gap and by 0.05 for 1.5B vs 8B size).

**Engineering cost:** 6-10 eng-days. HotpotQA bridge annotations exist (free). LoRA training on 1.5B is ~2 hr on one H100 for 90K examples. Serving cost: same as current LLM (LoRA adds negligible latency). Custom inference: LoRA adapter loaded alongside main model.

**P_actionable:** 0.58 (calibration-deflated from 0.78). High ceiling, moderate risk.

**Realistic ceiling:** 80% bridge-ID accuracy. At coverage=0.88, P(2hop) = 0.80 * 0.88 * 0.90 = 0.63. If coverage reaches 0.93 (warm), P(2hop) = 0.80 * 0.93 * 0.90 = 0.67.

**Why not rank higher despite best ceiling:** Requires training run, eng investment, HotpotQA licensing check for commercial use, and a dedicated pre-test (per feedback-drill-pretest-required) before authorizing cloud training spend. Cannot ship in a v1.1 sprint without the pre-test gate. Slides to v1.5 if pre-test fails.

---

### Rank 2 -- Option 2: Multi-Stage Cascade (NER + Substrate Frequency + LLM Verify)
**What it is:** Three-stage pipeline. Stage 1: apply a strong NER model (DistilBERT-NER or spaCy lg) to extract candidate entities from the question. Stage 2: rank candidates by how often each candidate entity appears as a stored binding in the substrate's relation table (substrate-frequency prior). Stage 3: if top-1 candidate confidence is below threshold, call LLM to verify top-3 candidates (single forward pass: "which of these is the bridge entity?").

**Mechanism:** Each stage contributes an independent signal. NER surfaces candidate spans with moderate recall (~80%) and low precision (~65%). Substrate-frequency re-ranks by plausibility: entities that appear in many substrate bindings are more likely to be real bridge entities than rare or hallucinated entities. LLM verify adds reasoning signal for ambiguous cases.

**Theoretical lift:** Fusion of three weak signals. NER recall 80% + substrate-frequency precision lift 10-15pp + LLM verify on remaining ambiguous 30% (LLM correct on 70% of those): combined accuracy ~72-76%.

**Engineering cost:** 3-5 eng-days. DistilBERT-NER is a drop-in HuggingFace model (30MB). Substrate frequency query is O(1) lookup in the existing binding table. LLM verify is a short prompt (10-20 tokens). No training required.

**P_actionable:** 0.52 (deflated from 0.67 by calibration penalty 0.15; stage 3 LLM verify for small models is uncertain per lit).

**Realistic ceiling:** 74% bridge-ID. At coverage=0.88, P(2hop) = 0.74 * 0.88 * 0.90 = 0.59. Reaches 0.61 at coverage=0.93. Does NOT reach 0.70 target without additional investment.

**Why rank 2:** No training required; fastest path to measurable lift. Combined with Option 3 (substrate-augmented lookup), can push P(2hop) to ~0.61-0.63 without any training. That is a meaningful improvement from the current ~0.54 ceiling even if it does not fully close the gap.

---

### Rank 3 -- Option 5: Pattern-B Algebraic Bridge Generation
**What it is:** Bypass NER entirely. Use the substrate's existing Pattern-B unbind to generate bridge candidates algebraically. Pattern-B: given query vector q, unbind to find top-k matching fillers in the stored bundle. At warm substrate, the stored bindings include (question_hop1, bridge_entity) pairs accumulated via Component F (bridge cache). The bridge prediction is: bridge = argmax_v cos(phi(v), B * phi(q)^{-1}).

**Mechanism:** This is structurally identical to how the substrate already resolves direct queries. The bridge prediction IS the Pattern-B retrieval result for the first hop. No LLM call, no NER pass. The bridge entity is the substrate's top-1 response to the first-hop sub-question.

**Theoretical lift:** At warm substrate (bridge coverage >= 85%), the algebraic bridge generation is limited by (a) whether the first-hop sub-question was correctly decomposed, (b) whether the bridge binding is stored at high confidence. Empirical state: Pattern-B HARD-PASS at acc=1.0 for k=2-8 (cycle 158). The limit is not unbind accuracy but bridge binding completeness. At coverage=85%, this method is correct 85% of the time on covered bridges. Uncovered bridges (15%) require fallback to NER.

**Engineering cost:** 0-2 eng-days. The mechanism already exists. The only engineering is: (a) use Pattern-B output as the bridge prediction instead of the NER output, (b) implement fallback to NER for low-confidence unbind results. No training, no external models.

**P_actionable:** 0.48 (deflated from 0.68; cold-start constraint is binding; warm substrate requires pre-seeding which adds deployment complexity).

**Realistic ceiling:** At warm substrate, 85-88% bridge-ID for covered entities. Combined with NER fallback for uncovered: (coverage * 0.87) + (1-coverage) * NER_acc. At coverage=0.85, NER_acc=0.65: 0.85*0.87 + 0.15*0.65 = 0.74 + 0.10 = 0.84 total. This is the highest ceiling of any option -- but requires warm substrate.

**Why rank 3 not 1:** Cold-start bridge-ID is still limited by NER (no warm substrate at deployment D0). The ceiling is only achievable at equilibrium (~Q=50K-100K). For v1.1 (cold-start benchmark), this option reads lower than Rank 1 and 2.

---

### Rank 4 -- Option 3: Substrate-Augmented Bridge Prediction (Relation Lookup)
**What it is:** The substrate stores (entity1, relation, entity2) triples as Pattern-A/B bindings. Bridge prediction = lookup: given question text, extract candidate entities (via any NER), then for each candidate, query: "does this entity appear in any stored relation?" If yes, and the relation aligns with the question's implicit relation, this candidate is promoted.

**Mechanism:** Substrate-frequency prior is a weaker version of Option 5. It uses the substrate's existing index to re-rank NER candidates without generating bridges algebraically. The key distinction: Option 3 re-ranks NER output; Option 5 replaces NER output.

**Theoretical lift:** Lift over raw NER: ~8-12pp precision increase by rejecting candidates not present in the substrate. At bridge coverage=0.85, recall is unchanged (correct bridge is in the substrate), precision improves from ~65% to ~73-77%.

**Engineering cost:** 1-2 eng-days. Pure lookup; no training; integrates with existing binding table.

**P_actionable:** 0.45. Moderate lift, easy to implement, works well as a component of Option 2 cascade.

---

### Rank 5 -- Option 7: Prompt-Optimized LLM Bridge Extraction
**What it is:** Better prompting of the existing 1.5B LLM for bridge entity identification. Chain-of-thought: "What entity in this question would I need to look up first to answer the question?" Few-shot examples of bridge identification. Output constraint: "Return only the entity name, nothing else."

**Mechanism:** Current LLM prompt treats bridge extraction as implicit (as part of broader question decomposition). Dedicated bridge-extraction prompt focuses the model on the specific task. Few-shot examples provide pattern matching.

**Theoretical lift:** Literature caution from search results: chain-of-thought is an emergent ability that underperforms in models below ~7B parameters. The 1.5B LLM is explicitly in the low-reliability CoT regime. Prompt optimization can still help via format constraints and few-shot pattern matching without CoT reasoning. Expected lift: 5-10pp over current 60-65% baseline, reaching 65-72%.

**Engineering cost:** 1-2 eng-days (prompt engineering; no infrastructure changes).

**P_actionable:** 0.40. Uncertain lift at 1.5B scale. Fast iteration but ceiling is low.

**Realistic ceiling:** 70% bridge-ID. At coverage=0.88: P(2hop) = 0.70 * 0.88 * 0.90 = 0.55. Marginally above current state.

---

### Rank 6 -- Option 1b: DistilBERT-NER (HF Token Classification)
**What it is:** Replace or augment regex NER with dslim/bert-base-NER (fine-tuned on CoNLL-2003). Drop-in HuggingFace model; token classification returning PERSON, ORG, LOC, MISC spans.

**Theoretical lift:** BERT-NER achieves F1=0.916 on CoNLL-2003; spaCy en_core_web_lg achieves ~0.895. On multi-hop QA bridge entities specifically, the gap between these may be smaller because HotpotQA bridge entities are predominantly PER and ORG (Wikipedia-domain). Expected: 65-72% bridge-ID (up from 60-65% with regex).

**Engineering cost:** 0.5 eng-days (pip install transformers; model ~0.25GB; inference latency ~10ms on CPU).

**P_actionable:** 0.38. Modest improvement; safe baseline upgrade.

---

### Rank 7 -- Option 1a: spaCy en_core_web_lg
**What it is:** Upgrade from the current regex NER to spaCy's large English model. spaCy lg uses a CNN-based pipeline; accuracy between spaCy sm and BERT-NER.

**Theoretical lift:** ~5pp over regex NER. Reaches ~65-68% bridge-ID. Well below the 75% target.

**Engineering cost:** 0.5 eng-days.

**P_actionable:** 0.35. Useful as a baseline; does not close the gap.

---

### Rank 8 -- Option 12: Substrate Adversarial Bridge Validation
**What it is:** After any bridge prediction (from NER or LLM), validate that the predicted bridge entity has at least one stored relation in the substrate. If not found in the substrate's binding table, reject and fall back to the next candidate.

**Mechanism:** This is a rejection filter, not a predictor. It removes hallucinated or spurious LLM predictions that have no substrate grounding. Benefit: reduces false-positive bridge predictions. Limitation: at cold start or for entities truly absent from the substrate, it may reject correct predictions (false negatives).

**Theoretical lift:** Lift depends on the false-positive rate of the upstream NER/LLM predictor. If 20% of current wrong predictions are hallucinated entities (not in the substrate), this filter catches those 20%, improving precision by ~8-12pp. Net effect depends on false-negative rate (correct bridges rejected because not yet in substrate).

**Engineering cost:** 0.5 eng-days.

**P_actionable:** 0.33. Defensive improvement; pairs well with any other option as a post-processing step.

---

### Rank 9 -- Option 11: Pre-Trained Bridge Predictor
**What it is:** Ship a pre-trained bridge classification model with the substrate product. Trained offline on HotpotQA + 2WikiMultiHopQA bridge annotations. Customers load it; no per-customer training needed. Analogous to pre-trained substrate initialization.

**Mechanism:** Structurally identical to Option 8 (LoRA bridge head) but framed as a shipped artifact rather than a per-deployment training step. The distinction is product-level, not technical.

**Theoretical lift:** Same ceiling as Option 8 (78-83% bridge-ID) but available from day 1 for any customer without training investment.

**Engineering cost:** 8-12 eng-days (train once; version and ship with substrate package; licensing/IP checks on HotpotQA commercial use). Higher cost than Option 8 due to productization overhead.

**P_actionable:** 0.30. High ceiling but requires significant one-time investment; suitable for v1.5 roadmap.

---

### Rank 10 -- Option 9: Multi-LLM Voting
**What it is:** Run N small LLMs independently on the bridge extraction task; take majority vote. E.g., run 1.5B Qwen + 1.5B Phi-3 + 1.5B Gemma in parallel; take the 2/3 majority bridge entity.

**Theoretical lift:** If three 1.5B LLMs each have 65% accuracy and their errors are independent, ensemble accuracy = P(2+ correct) = 3*(0.65^2)*(0.35) + 0.65^3 = 0.444 + 0.274 = 0.72. BUT: errors at 1.5B scale are NOT independent -- they are correlated on the same hard questions (same model family, same pre-training distribution). Effective ensemble gain is lower: ~68-70%.

**Engineering cost:** 3-5 eng-days (3x inference infrastructure, 3x latency or parallelized).

**P_actionable:** 0.28. Moderate lift, high latency cost, error-correlation degrades the theoretical gain.

---

### Rank 11 -- Option 10: Substrate-LLM RL (Reward for Bridge-ID leading to correct final answer)
**What it is:** Train the LLM with RL using the final multi-hop answer correctness as the reward signal for bridge-ID. Correct bridge -> correct final answer -> positive reward; wrong bridge -> wrong answer -> negative reward.

**Theoretical lift:** If training works, this closes the bridge-ID gap completely and optimizes jointly for the end-to-end objective. RL with sparse reward at 1.5B scale is feasible (RLHF papers show 1B+ models can be RL-tuned).

**Engineering cost:** 15-25 eng-days. Requires rollout infrastructure, reward model or oracle answer checker, stable training loop. Highest engineering cost of any option.

**P_actionable:** 0.22. High ceiling but very high engineering risk and cost. Calibration penalty hard: novel RL training at 1.5B with sparse reward, no prior empirical validation here.

**Realistic ceiling:** If successful, 80-85% bridge-ID. But P(training succeeds) = 0.4 (deflated from raw 0.6 by calibration penalty). Product-adjusted P = 0.40 * 0.82 = 0.33.

---

### Rank 12 -- Option 6: GNN Bridge Prediction
**What it is:** Build an entity graph from the substrate (nodes = entities, edges = stored relations). Train a Graph Neural Network to predict bridge entities: given a question embedding and the entity graph, predict which entity is the bridge.

**Theoretical lift:** GNN bridge prediction is well-studied (HGRAG, graph-of-thoughts). State-of-the-art GNN-based multi-hop systems achieve high recall on structured graphs. However, this requires a well-populated entity graph, which is the bridge coverage problem again.

**Engineering cost:** 20-30 eng-days. New infrastructure (graph construction, GNN training, online inference). Very high.

**P_actionable:** 0.18. High theoretical ceiling but maximum engineering cost. Overkill for v1.1. Relevant only for a full product rebuild targeting graph-structured KBs.

---

## Multi-Stage Composition Recommendation

The recommended combination for v1.1 is: **Option 2 (cascade) seeded by Option 1b (DistilBERT-NER) + Option 3 (substrate validation) + Option 5 (algebraic bridge generation at warm)**. Written as a pipeline:

```
bridge_predict(question, substrate):
    # Stage 1: token classification (drop-in)
    candidates = distilbert_ner(question)  # top-3 spans

    # Stage 2: substrate-frequency re-rank (lookup, O(1))
    candidates = substrate_frequency_rerank(candidates, substrate.binding_table)

    # Stage 3: algebraic bridge (if substrate warm)
    if substrate.bridge_coverage > 0.70:
        algebraic_bridge = pattern_b_unbind(question_embedding, substrate)
        if algebraic_bridge.confidence > theta_bridge:
            return algebraic_bridge.entity  # fast path

    # Stage 4: LLM verify (only for top-2 ambiguous cases)
    if max_confidence(candidates) < theta_nlp:
        verified = llm_verify_bridge(question, candidates[:2])
        return verified

    return candidates[0]
```

This composition is additive: each stage handles a different failure mode. DistilBERT-NER catches entities that regex misses. Substrate frequency rejects hallucinated entities. Algebraic bridge bypasses NER at warm substrate. LLM verify resolves genuine ambiguity. Empirical accuracy projection:

- Stage 1 only: ~68% (DistilBERT baseline)
- Stages 1+2: ~72-74% (precision lift from substrate rejection)
- Stages 1+2+3 at coverage=0.75: ~76-78% (algebraic bridge on covered 75%)
- Stages 1+2+3 at coverage=0.90: ~82-84% (algebraic bridge dominant)
- Full pipeline at coverage=0.90: ~83-85% (LLM verify adds 1-2pp on edge cases)

The Stage 3 contribution grows as bridge coverage accumulates. The v1.1 composition with warm substrate converges to Option 5 as the dominant path, with DistilBERT-NER + LLM-verify as fallbacks.

---

## Multi-Hop Accuracy Projection: Both Bottlenecks Closed

**Formula:** P(2hop) = P(bridge_id) * P(coverage) * P(unbind_given_hit)

P(unbind_given_hit) = 0.90 (HARD-PASS at cycle 158; stable).

**Scenario matrix:**

| Stage | bridge_id | coverage | P(2hop) | vs baseline (0.54) |
|-------|-----------|----------|---------|-------------------|
| Baseline (current) | 0.62 | 0.88 | 0.49 | -- |
| v1.1 Cascade (no warm) | 0.72 | 0.88 | 0.57 | +0.08 |
| v1.1 Cascade (warm=0.85) | 0.80 | 0.88 | 0.63 | +0.14 |
| v1.5 LoRA + warm=0.90 | 0.82 | 0.90 | 0.66 | +0.17 |
| v1.5 LoRA + warm=0.93 | 0.82 | 0.93 | 0.69 | +0.20 |
| v2.0 Full pipeline warm | 0.85 | 0.93 | 0.71 | +0.22 |

**Gap-to-target analysis:** Target is P(2hop) >= 0.70 (bridge-ID HARD-PASS criterion). The v1.5 row with warm substrate nearly reaches it (0.69). v2.0 reaches 0.71 under favorable assumptions. Reaching 0.70 requires BOTH bottlenecks close together: bridge-ID cannot be at 0.62 even if coverage is perfect (0.62 * 1.0 * 0.90 = 0.56). Coverage cannot be 1.0 even if bridge-ID is perfect (1.0 * 0.88 * 0.90 = 0.79 -- this one easily exceeds 0.70).

**Honest verdict:** The 0.70 target is reachable at v1.5/v2.0 deployment scale with warm substrate. It is NOT reachable from the current cold-start configuration (P_2hop ~ 0.49 with current 62% bridge-ID). The gap from 0.49 to 0.70 requires improvement on both axes simultaneously. The multi-hop revival is achievable -- it is not achievable in a single sprint.

---

## Cross-Thread Synthesis

**From self-improving routing drill (3x, 2026-06-07):** That drill established bridge COVERAGE grows to 90%+ at Q=100K via usage accumulation. The formula at that point was P(2hop) = 0.70 * 0.93 * 0.90 = 0.59 using bridge_id=0.70 as the denominator. This 2x drill reveals that 0.70 bridge-ID was assumed as a baseline -- but the actual baseline is 0.60-0.65. The prior drill therefore overestimated equilibrium multi-hop accuracy. Corrected equilibrium at Option 2 cascade + warm coverage: P(2hop) = 0.80 * 0.93 * 0.90 = 0.67 (Option 8 LoRA path). The self-improving architecture's latency improvement claim (cold to hot 4.6x) is unaffected because that is a routing-speed metric, not a bridge-ID metric.

**From cycle 157 entity_bridge_decomp HARD-FAIL:** Regex NER failure is confirmed; LLM 1.5B at 60% is the empirical baseline. This drill's stack-rank is calibrated to that empirical starting point.

**From encoder upgrade finding (e5-large 0.444 < bge-large):** Encoder upgrade alone does not help bridge-ID because bridge-ID is not a retrieval problem -- it is a span-extraction or entity-recognition problem. The encoder processes the retrieved document; bridge-ID must happen before the retrieval (to know what to retrieve). These are different problems in different positions in the pipeline. This invalidates any expectation that fixing the encoder will incidentally fix bridge-ID.

**From BridgeRAG (arXiv 2604.03384, April 2026):** BridgeRAG conditions candidate ranking on bridge evidence using a tripartite scorer s(q, b, c). R@5 of 0.9875 on HotpotQA. This is a dense-retrieval system, not a substrate system, but the bridge conditioning insight (bridge entity enables second-hop candidate expansion) is directly analogous to Option 2 (cascade) and Option 5 (algebraic bridge) in this drill. BridgeRAG uses a bridge predictor as a first step -- their system is training-free (bridge evidence extracted from first-hop retrieved docs, not from a dedicated bridge-ID model). This is structurally similar to Option 5 (algebraic bridge from first-hop unbind). The convergence is encouraging.

---

## Engineering Cost vs Lift Summary

| Option | Lift (pp bridge-ID) | Eng-Days | P_actionable | When |
|--------|---------------------|----------|--------------|------|
| 8 LoRA bridge head | +18-20pp (60 to 78-80%) | 6-10 | 0.58 | v1.5 (requires pre-test) |
| 2 Multi-stage cascade | +12-14pp (60 to 72-74%) | 3-5 | 0.52 | v1.1 (no training) |
| 5 Algebraic bridge (warm) | +20-25pp at coverage=0.85 | 0-2 | 0.48 | v1.1 warm (no training) |
| 3 Substrate validation | +8-12pp (precision) | 1-2 | 0.45 | v1.1 (component of cascade) |
| 7 Prompt-optimized LLM | +5-10pp | 1-2 | 0.40 | v1.1 (baseline improvement) |
| 1b DistilBERT-NER | +5-8pp | 0.5 | 0.38 | v1.1 (drop-in) |
| 1a spaCy lg | +3-5pp | 0.5 | 0.35 | v1.1 (minimal lift) |
| 12 Adversarial validation | +5-8pp (precision filter) | 0.5 | 0.33 | v1.1 (post-processing) |
| 11 Pre-trained predictor | +18-20pp | 8-12 | 0.30 | v1.5+ |
| 9 Multi-LLM voting | +6-8pp effective | 3-5 | 0.28 | Not recommended |
| 10 RL end-to-end | +20-25pp (if converges) | 15-25 | 0.22 | v2.0 |
| 6 GNN bridge prediction | +15-20pp | 20-30 | 0.18 | Not for v1.x |

---

## Is This Gap Closeable? Honest Verdict

Yes, but not in one sprint. The honest framing:

**Short answer:** From 60% bridge-ID to 75%+ requires one of (a) dropping in DistilBERT-NER + substrate cascade [v1.1, ~3-5 eng-days, gets to ~74%], or (b) training a LoRA bridge head [v1.5, ~6-10 eng-days, gets to ~78-80%]. Option (a) gets you 74% without training; option (b) gets you 78-80% with training.

**Combined with coverage:** At v1.1 with cascade bridge-ID=0.74 and coverage=0.90, P(2hop) = 0.74 * 0.90 * 0.90 = 0.60. This exceeds the current cycle-157 empirical result of ~0.54 by 6pp. It does not reach 0.70 yet.

**At v1.5** with LoRA bridge-ID=0.80 and warm coverage=0.92, P(2hop) = 0.80 * 0.92 * 0.90 = 0.66. Getting from 0.66 to 0.70 requires full pipeline composition (algebraic bridge + LoRA + warm substrate together).

**The gap is not a fundamental impossibility.** It is an engineering effort gap. The math closes at v1.5/v2.0 deployment scale with warm substrate. The cold-start benchmark will not show 0.70+ unless LoRA is deployed from day 1 with the pre-trained bridge predictor (Option 11). Customer-facing 0.70+ multi-hop accuracy requires: (a) LoRA bridge head pre-trained and shipped, AND (b) warm substrate (K queries processed before benchmarking). Benchmarking from cold start with the current system will not reach 0.70.

---

## v1.1 / v1.5 / v2.0 Sequencing

### v1.1 Sprint (3-5 eng-days, no training)
1. Run the 200-question pre-test (2 hr, described above).
2. Drop in DistilBERT-NER as the NER stage (0.5 eng-days).
3. Implement substrate-frequency re-rank as the second stage (1-2 eng-days).
4. Implement Pattern-B algebraic bridge generation as the fast path when confidence > threshold (1-2 eng-days).
5. Add adversarial substrate validation as a post-processing rejection filter (0.5 eng-days).
6. Expected outcome: bridge-ID ~72-76%, P(2hop) ~0.57-0.61 at cold start.

**Pre-test gate:** Pre-test must show DistilBERT-NER >= 72% on bridge-200 before committing to the cascade architecture. If DistilBERT-NER < 65%, pivot to LoRA path immediately (skip cascade, go to Option 8 as v1.1 priority).

### v1.5 Sprint (6-10 eng-days, one training run)
1. Prepare HotpotQA bridge entity training data (1 eng-day; data is public).
2. Fine-tune LoRA bridge head on 1.5B LLM (2 hr cloud, 1 eng-day setup + monitoring).
3. Evaluate on held-out 500 questions; confirm >= 78% accuracy.
4. Integrate with v1.1 cascade as the Stage 3 replacement for LLM-verify.
5. Expected outcome: bridge-ID ~78-82%, P(2hop) ~0.63-0.68 at warm substrate (Q=50K+).

### v2.0 Horizon (16+ eng-days, full system)
1. Pre-train bridge predictor as a shipped model artifact (Option 11).
2. Ship with warm substrate initialization (pre-seeded bridge bindings from a standard QA corpus).
3. Integrate substrate-LLM RL loop for end-to-end optimization (Option 10, lower priority).
4. Expected outcome: bridge-ID ~82-85%, P(2hop) ~0.70-0.74 at warm substrate.

---

## Customer Pitch Implications

The multi-hop revival arc has a product narrative:

v1.1: "We fixed the NER bottleneck. Multi-hop accuracy improved from ~54% to ~60% on HotpotQA. Our system now ties baseline RAG on multi-hop." This is an honest claim at cold-start benchmark.

v1.5: "With a fine-tuned bridge extractor, we exceed RAG on multi-hop. Our system reaches 65-68% on HotpotQA vs RAG baseline of 60-63%." This requires one training run.

v2.0 (warm deployment): "At deployment scale, the substrate self-improves its bridge coverage. Multi-hop accuracy reaches 70%+ after 50K queries -- without any model updates. Accuracy improves as customers use the system. RAG does not have this property." This is the moat story. It requires warm substrate evidence.

The honest positioning: v1.1 and v1.5 are "competitive with RAG" on multi-hop, not "superior." The substrate's compositional SUPERIORITY claim only holds at v2.0 deployment scale with warm substrate + LoRA bridge. Over-claiming before that point violates the no-smoke, brutal honesty rule.

---

## Substrate-Product Implications

1. The multi-hop revival requires investment in the bridge-ID layer. It is not a free byproduct of substrate architecture improvements.
2. The algebraic bridge generation (Option 5) is the long-run moat: at warm substrate, no external NER model is needed, no LLM call is needed for bridge identification, and the accuracy exceeds all NER-based approaches. Engineering the fast-path fallback to algebraic generation is the architectural priority.
3. The pre-test (bridge-200) is cheap and decisive. It should run before any v1.1 engineering begins to confirm which path (cascade vs LoRA) is the faster route to 75% bridge-ID.
4. The 0.70 P(2hop) target is achievable at v1.5/v2.0 but NOT at v1.1 cold-start without pre-trained bridge head.

---

## Citations (Verified)

1. BridgeRAG: Training-Free Bridge-Conditioned Retrieval for Multi-Hop QA. arXiv:2604.03384, April 2026. [Link](https://arxiv.org/html/2604.03384v1)
2. LLM-NER: Advancing NER with LoRA+ Fine-Tuned LLMs. ResearchGate 2024. [Link](https://www.researchgate.net/publication/394575074_LLM-NER_Advancing_Named_Entity_Recognition_with_LoRA_Fine-Tuned_Large_Language_Models)
3. ERA-CoT: Improving Chain-of-Thought through Entity Relationship Analysis. ACL 2024. [Link](https://aclanthology.org/2024.acl-long.476.pdf)
4. Retrieval-Reasoning Processes for Multi-hop QA: Four-Axis Design Framework. arXiv:2601.00536, 2026. [Link](https://arxiv.org/html/2601.00536v1)
5. PRISM: Agentic Retrieval with LLMs for Multi-Hop QA. arXiv:2510.14278, 2025. [Link](https://arxiv.org/html/2510.14278v1)
6. Instruction Finetuning LLaMA-3-8B with LoRA for Financial NER. arXiv:2601.10043, 2026. [Link](https://arxiv.org/abs/2601.10043)
7. Question Decomposition for Retrieval-Augmented Generation. arXiv:2507.00355, 2025. [Link](https://arxiv.org/pdf/2507.00355)
8. GenDec: Robust Generative Question Decomposition for Multi-hop Reasoning. arXiv:2402.11166, 2024. [Link](https://arxiv.org/html/2402.11166v1)
9. Recent Advances in Named Entity Recognition: Comprehensive Survey. arXiv:2401.10825, 2024. [Link](https://arxiv.org/pdf/2401.10825)
10. NER4all: Using LLMs for Low-Effort High-Performance NER. arXiv:2502.04351, 2025. [Link](https://arxiv.org/pdf/2502.04351)
11. Sample Size Considerations for Fine-Tuning LLMs for NER. JMIR AI, 2024. [Link](https://ai.jmir.org/2024/1/e52095)
12. Is Hope a Person or Idea: Pilot Benchmark for NER comparing Traditional NLP Tools and LLMs. arXiv:2509.12098, 2025. [Link](https://arxiv.org/html/2509.12098v1)

**Verified citation count: 12**

---

**P_theoretical = 0.62 | P_empirical = 0.35 | Calibration penalty applied (-0.20 from raw) | Novel-synthesis cap honored at 0.50**

**Next drill candidate:** Option 8 LoRA bridge head pre-test design (after bridge-200 pre-test passes); OR substrate-side algebraic bridge fast-path integration spec.
