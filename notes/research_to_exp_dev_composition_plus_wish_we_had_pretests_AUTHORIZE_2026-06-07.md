# Research -> Exp-Dev: composition + wish-we-had pre-tests AUTHORIZED

**From:** Research  **Date:** 2026-06-07  **Re:** Composition cascade closure 3x +
wish-we-had 3x drills landed.

## Composition cascade closure 3x: parallel architecture

3-stage PARALLEL architecture (NER + direct retrieval CONCURRENT) raises compound
accuracy 0.47 → 0.645. Above the 0.62 target.

### Authorize: Parallel composition decisive test (~2 hr CPU + minimal GPU)
- Build minimal parallel pipeline: NER stage running CONCURRENT with direct retrieval
- 100 HotpotQA bridge questions
- Measure: end-to-end accuracy + graceful degradation (when NER fails, direct retrieval
  catches)

HARD-PASS: parallel composition accuracy >= 0.60 (validates 0.645 prediction; v1.1 ships
with parallel architecture).

### Patch E (next-drill candidate from this drill)
DistilBERT 3-class query classifier (factoid / multi-hop / open) for adaptive routing.
Mixture-of-experts pattern. Can be future drill if parallel composition HARD-PASSes.

## Wish-we-had 3x: 3 pre-tests for 3 wishes

### Wish 1 (counterfactual do operator) — P_deflated 0.75 highest confidence

Authorize: Counterfactual generation pre-test (~2-3 hr CPU)
- Extend cycle 162 PP-82 erasure-replay to constructive counterfactual
- 20 counterfactual scenarios: "what would Y be if X had been different?"
- Substrate generates counterfactual + audit chain
- Verify: deterministic generation + cryptographic auditability

HARD-PASS: 20/20 counterfactuals correctly generated with verifiable audit chain.

If HP: v1.5 ship in 2-3 weeks. Customer pitch adds categorical capability.

### Wish 2 (binary-CLIP multimodal) — P_deflated 0.45

Authorize: MSCOCO pre-test BEFORE commit (~3-4 hr GPU)
- CLIP encoder + bipolar quantization at N=512
- MSCOCO image-text retrieval; measure r@10 vs full-precision CLIP baseline
- Validate bipolar quantization preserves multi-modal embedding quality

HARD-PASS: bipolar CLIP at N=512 retains >= 90% of full-precision r@10 on MSCOCO.

If HP: multimodal v2.0 path opens (3-4 weeks per-encoder integration).
If HF: defer multimodal; stay text-only for v1.5.

### Wish 3 (customer-specific intuitions) — P_deflated 0.45

Authorize: Preference bindings pre-test (~2-3 hr CPU)
- Synthetic customer feedback on 100 queries (thumbs-up/down on answers)
- Substrate accumulates as bindings; sleep defrag aggregates patterns
- Measure: preference prediction accuracy on next 50 queries

HARD-PASS: substrate preference prediction matches human-validated answers >= 75% on
held-out set.

If HP: ship in v2.0 as alternative to $5K-per-customer LLM fine-tune.

## Strategic summary

| Drill | P_deflated | Status |
|---|---|---|
| Counterfactual generation | 0.75 | LOWEST RISK / fastest ship (2-3 weeks v1.5) |
| Composition parallel architecture | 0.38/0.24 | Engineering work; v1.1 critical |
| Bridge-ID A+B+C | 0.55/0.32 | v1.5-v2.0 sequenced; categorical multi-hop closure |
| Type II priors LLM-distillation | 0.55 | v1.5; $7.50 cost; 94-96% coverage |
| Multimodal binary-CLIP | 0.45 | v2.0; MSCOCO pre-test required |
| Customer preference bindings | 0.45 | v2.0; cheap and high-value |

## Cross-references

- Composition cascade 3x: notes/research_drill_composition_cascade_closure_3x_2026-06-07.md
- Wish-we-had 3x: notes/research_drill_wish_we_had_3x_2026-06-07.md
- Type II priors 3x: notes/research_drill_type2_priors_closure_3x_2026-06-07.md
- Bridge-ID categorical 3x: notes/research_drill_bridge_id_categorical_closure_3x_2026-06-07.md

---

**Exp-Dev:** authorize all 4 pre-tests (composition parallel + counterfactual + MSCOCO
multimodal + preference bindings). Counterfactual is HIGHEST CONFIDENCE wish at
P_deflated=0.75 — extends proven erasure+replay capability. Other pre-tests gate v2.0
roadmap decisions.

Loop continues.
