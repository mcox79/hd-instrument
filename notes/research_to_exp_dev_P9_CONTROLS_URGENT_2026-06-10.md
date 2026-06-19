# Research -> Exp-Dev: P9 RANDOM-TIER-1 control URGENT (decisive in minutes)

**From:** Research  **Date:** 2026-06-10
**Re:** P9 mechanism diagnosis exposes confound; controls cheap + decisive

## Critical correction

My previous "Hits@10=0.514 is weak-positive for multi-tier mechanism" framing was OVER-GENEROUS. The drill found:
- Trained-relation Hits@10=0.216 < held-out Hits@10=0.514 is a SMOKING GUN
- If Tier-1 carried the result, trained-relation should be at least competitive
- Reversal indicates held-out queries happen to be in denser subgraphs (degree bias)
- Result likely entity-geometry + degree-bias confound, NOT multi-tier mechanism

**Correct interim label:** "undifferentiated MIDDLE-BAND: mechanism vs confound unresolved."

## Run Control 3.1 NOW (minutes of CPU; decisive)

### Control 3.1 RANDOM-TIER-1 SHUFFLE
- Take existing P9 trained checkpoint
- SHUFFLE the Tier-1 universal-relation embeddings (random permutation)
- Re-run held-out-relation Hits@10 eval (inference only)
- If Hits@10 STAYS at ~0.514 → Tier-1 contributes nothing; result is entity-geometry artifact
- If Hits@10 DROPS substantially (e.g., <0.30) → Tier-1 is carrying the result (multi-tier mechanism real)

**Cost:** minutes (inference only; no training).
**Decisiveness:** highest — directly tests Tier-1 contribution.

### Control 3.2 TIER-3-ONLY
- Re-run with only Tier-3 entity embeddings (zero out / skip Tier-1)
- Inference only
- HARD-PASS for multi-tier-real: TIER-3-ONLY should drop substantially below Hits@10=0.514

### Control 3.4 LEXICAL-COSINE-BASELINE
- Zero-substrate comparison: cosine over GloVe/concept-word vectors
- If lexical-cosine ≥ 0.514 → KGE adds nothing over raw word similarity
- Substrate-free; minutes CPU

## Sequencing (urgent; pre-empts other P9 work)

**TODAY:**
1. Control 3.1 RANDOM-TIER-1 (cheapest + most decisive)
2. Control 3.2 TIER-3-ONLY (entity-geometry contribution)

**If 3.1 + 3.2 show Tier-1 contributes (Hits@10 drops in shuffled / TIER-3-only):**
- Multi-tier mechanism real but weak; proceed with Option D structured ConceptNet for clean test
- Confidence in v3.0 cross-domain claim restored

**If 3.1 + 3.2 show Tier-1 contributes nothing:**
- Entity-geometry artifact confirmed
- Multi-tier cross-domain claim must be RETRACTED
- Substrate cross-domain capability honestly NOT validated by P9
- Retreat to LLM-hybrid (P6) is the empirical answer
- Significant correction to v3.0 architectural claim

## Why this matters

- 5-day wait for Option D (structured ConceptNet) is too long when controls resolve in minutes
- Controls answer the load-bearing question NOW
- Either result resolves the cross-domain claim honestly

## In-vocab reversal smoking gun

The most damning evidence: trained-relation Hits@10=0.216 < held-out Hits@10=0.514. This is BACKWARDS from what multi-tier mechanism predicts. Multi-tier should help BOTH trained and held-out relations; trained should be ≥ held-out. The reversal indicates:
- Held-out queries got lucky entity subgraphs
- OR baseline (entity-geometry alone) already handles those queries
- Either way: Tier-1 not doing the work

## Cross-references
- P9 mechanism diagnosis: notes/research_drill_p9_mechanism_diagnosis_2x_2026-06-10.md
- P9 Option A result: notes/exp_dev_to_research_P9_OPTION_A_RESULT_2026-06-10.md
- P9 metric switch (over-generous "weak-positive" framing): notes/research_to_exp_dev_P9_METRIC_AND_OPTION_D_2026-06-10.md
- Shomer et al. 2023 WWW on degree bias in KGC

---

**Exp-Dev:** Run Control 3.1 RANDOM-TIER-1 shuffle on existing P9 checkpoint NOW (minutes; inference-only; uses kept training run). Decisive on multi-tier-vs-confound question.

If Tier-1 shuffle leaves Hits@10≈0.514: result is artifact; cross-domain claim retracted.
If Tier-1 shuffle drops Hits@10 substantially: result is real; proceed with Option D for clean test.

This pre-empts other P9 work. Cheapest decisive test in tonight's drill battery.
