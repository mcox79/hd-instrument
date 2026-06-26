# MH Revival ANCHOR 1: Feature-Matching Regime Diagnostic (n=2)

## Anchor
mh_revival_feature_regime_diagnostic_v1

## Queue
remote_cpu_queue (1 CPU-hr cheapest; per USER directive routing)

## Script
experiments/exp_mh_revival_feature_regime_diagnostic_v1.py

## Source
- Research drill: notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md
- Handoff: notes/exp_dev_handoff_research_modern_hopfield_revival_slow_built_basins_2026-06-26.md (ANCHOR 1)
- Prior failure anchor: gap3_modern_hopfield_prototype_attractor_v1 (MH_PROTO=0.22, MH_CONT=0.26 in
  prototype/softmax regime).

## Scientific question
Does the SAME Modern Hopfield architecture with `n=2` (Krotov feature-matching regime; many basins
cooperate) outperform `n=20` (prototype/softmax regime; one basin dominates) on the SAME substrate
state that just produced MH_PROTO=0.22?

Per Research drill Section 1: Krotov-Hopfield 2016 explicitly characterizes the model as a family of
energy functions parametrized by polynomial order `n`. Small n = many low-overlap memories cooperate;
large n -> softmax = one high-overlap pattern dominates. Substrate has 20 weak instances per
category; signal margin ~0.10. Large beta with 0.10 signal margin is structurally a noise amplifier.
Feature regime should match better.

## Mechanism
For each category c with training instances {x_1, ..., x_K}, given heldout query q:
```
overlap_i = <q, x_i>                       (per training instance, NOT per prototype)
readout   = sum_i x_i * F(overlap_i)        where F(s) is polynomial s^n / Z or softmax(beta * s)
```
Classify by per-category aggregate readout. Different `n` values produce different regimes:
- n=2  = classical Hopfield / feature regime (many memories cooperate)
- n=4  = mild dense memory
- n=10 = approaching prototype
- n=20-ish (softmax) = the prior failure regime (control rail)

## Arms (5)
- ARM_BASELINE_NO_SCHEMA         : Cell 1 nearest-train-neighbor (sanity rail)
- ARM_HRR_BUNDLE_PROTOTYPE       : Cell 1 cross-cell rail (privileged cat_vec; upper-bound)
- ARM_HOPFIELD_N2                : feature regime; many memories cooperate (the PRIMARY hypothesis)
- ARM_HOPFIELD_N4                : intermediate polynomial regime
- ARM_HOPFIELD_N10               : approaching prototype regime
- ARM_HOPFIELD_N20_SOFTMAX       : prior MH_PROTO failure-regime control rail

## Pre-registered bands (LOCKED via module-init assert)
- HARD_PASS: ARM_HOPFIELD_N2 >= 0.50 heldout AND >= +0.15 over ARM_HOPFIELD_N20_SOFTMAX (the prior
  failure 0.22 baseline).
  -> Interpretation: regime error confirmed; substrate already has the data to do better than 0.22;
     the cell that just failed picked the wrong polynomial order.
- HARD_FAIL: ARM_HOPFIELD_N2 within 0.05 of ARM_HOPFIELD_N20_SOFTMAX (both around 0.22).
  -> Interpretation: regime is not the issue; the mechanism class genuinely cannot work on
     substrate's existing W. Pivot to write-side slow-building (STC cell ANCHOR 2).
- MIDDLE_BAND [0.35, 0.50]: PARTIAL. Feature regime helps but not chain-grade margin. Queue follow-up.
- HARD_FAIL_HARNESS_CONFOUND: ARM_HRR_BUNDLE_PROTOTYPE drifts > 0.03 from Cell 1 0.4733 (full mode)
  or 0.58 (seed=11 smoke) -- harness changed; abort interpretation.

## Config (matches gap3_modern_hopfield_prototype_attractor_v1 exactly for cross-cell rail)
- N = 8192
- 5 categories x 20 train + 10 heldout
- chance = 0.20
- CATEGORY_SIGNAL_FRAC = 0.005 (cross-cell rail)
- seeds_full = [11, 13, 19]
- seeds_smoke = [11]

## Substrate disciplines
- ENCODER_PROVENANCE = "SUBSTRATE_NATIVE" (HRR circular convolution; no LLM)
- zero_llm_calls_at_inference = True
- per-arm metrics per Fix #28
- per-seed checkpoint per PROT-021 (timeout < 14400s so not strictly required but baked-in)

## Self-test formulas
- T1: HRR bind/unbind cosine >= 0.80
- T2: Hopfield readout n=2 recovers training-instance under low noise
- T3: At very low beta or n=2, readout degenerates to mean-weighted aggregate
- T4: bands LOCKED + CATEGORY_SIGNAL_FRAC matches Cell 1 (0.005)
- T5: cross-cell rail value (Cell 1 reference 0.4733) encoded
- T6: 5-arm discriminator non-degenerate on synthetic smoke

## Timeout estimate
- Mechanism: per heldout (50 queries) x per arm (4 Hopfield arms) x per category (5) x per instance
  in category (20) = ~20k cosines per heldout = O(20k * 50 * 4) ~ 4M dot-products at D=8192.
  Vectorized: ~10s/seed; non-vectorized ~60s/seed.
- smoke wall expected ~5-15s (single seed; vectorized matmul over (K_total=100, D=8192))
- FULL/smoke scaling: 3 seeds; same N; same arms count -> scaling factor ~3-4x.
- Estimate: ceil(1.5 * 15s * 3) = ~70s; budget 600s = 10min for safety + queue overhead.
- Per USER directive: 1 CPU-hr cheapest test, route to remote_cpu_queue.
- timeout_s = 3600 (1h budget; well under 14400s PROT-021 threshold)

## Importance
Cheapest decisive test of regime-vs-mechanism hypothesis. ~1 CPU-hr. If HARD_PASS, substrate-product
win without new architecture (just change polynomial order). If HARD_FAIL, slow-build (STC ANCHOR 2)
becomes the critical path. Either way, 2-hour wall to discriminate.

## Atomization on HARD_PASS
- atom: modern_hopfield_feature_regime_substrate_n2_outperforms_prototype
- hdlab primitive update: hdlab/iterative_attractor.py -- add feature-matching n-parametric variant
