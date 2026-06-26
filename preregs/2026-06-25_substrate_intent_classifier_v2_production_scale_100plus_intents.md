# Pre-registration: substrate_intent_classifier_v2_production_scale_100plus_intents

**Date:** 2026-06-25
**Anchor:** substrate_intent_classifier_v2_production_scale_100plus_intents
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [11, 13, 19]

## Why this cell exists

Research drill 2026-06-25 EXT-3: substrate intent classifier scaling to 100+
intents.

`a1_substrate_intent_classifier_v1` is chain-grade at 50 intents (acc=0.754;
maj_mult=4.62; rand_mult=5.19; p95=0.54ms; n_llm=0). Production intent
classification often needs 100-1000+ intents (customer support, multi-domain
assistants, slot-filling agents). P=0.65 per Research drill.

## Mechanism

Reuse prototype-bundle classifier pattern from `exp_a1_substrate_intent_classifier_v1`:
- Bipolar per-intent prototype codebook
- Hebbian-bound W = sum_q outer(prototype[label_q], question_hd[q]) / N_DIM
- Predict: argmax(prototype_codebook @ W @ question_hd)

Sweep n_intents in {50 (rail), 100, 200, 500, 1000}. Per n_intents, 3 ARMs:
- ARM_SUBSTRATE_INTENT (the cell's mechanism)
- ARM_RANDOM_BASELINE (uniform random; chance = 1/n_intents)
- ARM_MAJORITY_BASELINE (always predict most-frequent training intent)

## Scientific question

How many intents can the substrate distinguish at chain-grade (acc >= 0.65)
with cv <= 0.07 and p95 latency <= 5ms?

## Pre-registered bands

**HARD_PASS_PRODUCTION_INTENT_SCALE:**
- SUBSTRATE acc >= 0.65 at n_intents = 500
- AND p95 latency <= 5 ms at n_intents=500
- AND cv <= 0.07 across seeds at n_intents=500
- AND n_llm_calls == 0
  (substrate scales to 500-intent classification at production latency)

**CHAIN_GRADE_AT_CLIFF_X:**
- SUBSTRATE acc >= 0.65 at SOME n_intents in {100, 200, 500} with cv <= 0.07
- but doesn't pass the 500-intent floor
  (substrate has a measurable cliff X; chain-grade up to that X)

**HARD_FAIL_CLIFF_AT_100:**
- SUBSTRATE acc < 0.55 at n_intents=100
  (doesn't extend beyond the 50-intent rail; mechanism is at envelope at 50)

**SANITY_RAIL_AT_50_INTENTS:**
- SUBSTRATE acc in [0.65, 0.85] at n_intents=50
  (reproduces a1 cell's chain-grade rail acc=0.754 +/- 0.10)

**RAIL_SANITY_BREACH:**
- 50-intent acc outside [0.65, 0.85]; cell not interpretable

## Calibration rationale

- 0.65 floor at 500 intents per Research drill calibration: substrate's
  prototype-bundle capacity at N=8192 K_SET=20 per intent gives
  K_max ~ N / (k * V * K_SET) = 8192 / (2 * V * 20). At V=500, ratio = 0.41
  (below safe; mild degradation expected). At V=200, ratio = 1.02 (right at
  envelope; should still pass).
- 5ms p95: substrate matmul at N=8192 is sub-ms; the 5ms ceiling allows
  encoder overhead + classifier scoring at production scale.
- cv <= 0.07 per substrate deterministic-per-seed expectation.

## Q-discipline (BIAS-Q: suspect 1.000 results)

At n_intents=50 if acc >= 0.95, suspect over-fit to procedural templates.
Verify by inspecting per-seed values; if all seeds saturate, raise as
methodology-confound (test templates may be too similar to train templates).
Honest expectation per a1 rail: 0.65-0.85 at 50 intents.

## Capacity-feasibility analysis (Frady-Sommer)

- N=8192. K_SET=20 train samples per intent. K_max ~ N / (k * V * K_SET).
- V=50: ratio = 8192/(2*50*20) = 4.1 -- safe in chain-grade envelope.
- V=100: ratio = 2.0 -- safe with margin.
- V=200: ratio = 1.0 -- right at envelope; expect slight degradation.
- V=500: ratio = 0.4 -- 2.5x below safe; expect mid-band acc 0.50-0.70.
- V=1000: ratio = 0.2 -- 5x below safe; expect degraded acc 0.35-0.55.

Predicted CHAIN_GRADE cliff: 200-500 intents.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix; PROT-018 does not apply.

## Timeout estimate

Smoke ~ 30s estimated at N=2048, 1 seed, n_intents_sweep=[50, 100], 25 test
queries per intent.
FULL: N=8192, 3 seeds, n_intents in [50, 100, 200, 500, 1000], 100 test
queries per intent. Encoder + Hebbian train + per-query latency.
Scaling: encode is O(M_total); train is O(M_total * N); predict is O(N).
Total per-seed M_total at full = sum(n * (20+100)) = 120 * (50+100+200+500+1000) = 222000
encode/predict pairs.
formula: ceil(1.5 * 30 * (8192/2048) * (3/1) * 5_n_intents)
       = ceil(1.5 * 30 * 4 * 3 * 5) = 2700s
budget timeout_s = 3000 (50 min).
timeout_s = 3000

## Provenance rail

SUBSTRATE acc at n_intents=50 must reproduce a1 chain-grade rail acc=0.754
+/- 0.10 (sanity rail [0.65, 0.85]). The cell uses a DIFFERENT procedural
corpus than a1 (action-object procedural vs HotpotQA/NQ/ConceptNet); the
sanity rail confirms the substrate mechanism is regime-stable across corpus
shifts.

## Cross-cell apples-to-apples

Seeds [11, 13, 19] cross-cell consistent with EXT-1, EXT-6, partition_routing
v2. The 50-intent rail is a self-rail (this cell's own internal sanity check),
not a cross-cell apples-to-apples to a1.
