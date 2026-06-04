# Prereg: substrate_curriculum_learning_rung1_tinychar_v1

**Date:** 2026-06-04
**Routing:** Phase B rung-1 (overnight batch 2026-06-03, Section 3)
**Queue:** remote_cpu_queue
**Script:** experiments/exp_substrate_curriculum_learning_rung1_tinychar_v1.py

## Scientific Question

Does substrate-scored curriculum ordering improve val BPC for a gradient-trained tiny char-LM versus random batch order?

## Design

- Model: 2-layer TinyGRU (testbed.curriculum.training_loop), hidden=64
- Conditions: [random, substrate]
- Substrate: SubstrateCurriculumPolicy (N=256), hebbian_write + retrieval_cosine for least-redundant batch selection
- 2000 steps per condition, 3 seeds, corpus: wikitext2 char-level

## N-suffix declaration (PROT-018)

No `_nN` suffix. SUBSTRATE_N=256 is the production substrate observer dim (not a primary sweep axis). Rationale: this is a curriculum-ordering experiment; the substrate is an observer, not the trained model.

## Pre-registered Bands

- **HARD-PASS:** curriculum beats random by > 5% on val BPC (relative: (random_bpc - curr_bpc) / random_bpc > 0.05) AND 3/3 seeds AND finite BPC
- **MIDDLE:** 2-5% gain OR 2/3 seeds
- **HARD-FAIL:** curriculum matches or trails random (gain <= 2%)

## Timeout estimate

Smoke: 2.5s total (2 seeds x 2 conditions x 80 steps)
FULL: 2000 steps/condition, 3 seeds, scaling_exp=1.0
`timeout_s = ceil(1.5 * 2.5/4 * (2000/80) * (6/4)) = ceil(1.5 * 0.625 * 25 * 1.5) = ceil(35.2) -> 300s`
Conservative with dataset loading: **timeout_s = 1800**

## Smoke Result (2026-06-04)

- HARD_FAIL at smoke scale (gain_mean=0.13%, well below 5% threshold)
- Expected at tiny N=32, 80 steps: substrate barely differentiates batches yet
- Instrumentation selftest PASSED (all 5 assertions)
- Wall: 2.5s smoke
