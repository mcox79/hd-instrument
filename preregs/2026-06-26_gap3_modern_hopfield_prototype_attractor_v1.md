# Pre-registration: gap3_modern_hopfield_prototype_attractor_v1

**Date:** 2026-06-26
**Anchor:** gap3_modern_hopfield_prototype_attractor_v1
**Queue:** local_cpu_queue (CPU-only numpy; ~1 CPU-sec per seed full; whole cell ~1 sec)
**N:** 8192, **Seeds:** [11, 13, 19], **Categories:** 5, **Instances/cat:** 20 train + 10 heldout

## Scientific question

Cell 1 (substrate_cortical_schema_extraction_compositional_generalization_v1) landed MIDDLE_BAND with ARM_FEATURE_BASED_SCHEMA heldout_top1=0.4733 vs ARM_NO_SCHEMA_BASELINE=0.3733 (+0.10 lift, 1.27x). Research drill `notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md` argues the lift is real but caps at ~0.5 because HRR linear-bundle prototypes have crosstalk-noise floor of O(sqrt(K-1)/sqrt(N)) when heldout queries match by feature similarity not membership (Plate 1995 + Schlegel 2021). The proposed escape: replace linear-mean prototype with non-linear softmax-beta-weighted Modern-Hopfield basin-attractor prototype (Krotov-Hopfield 2016 dense associative memory; Ramsauer 2020 transformer-equivalent). Brain analog: cortical schema basins sharpen with more exemplars (non-linear depth), unlike linear bundles that get noisier.

## Arms (5)

- `ARM_BASELINE_NO_SCHEMA` -- nearest-train-neighbor (Cell 1 identical); sanity rail; expected ~0.37 mean
- `ARM_HRR_BUNDLE_PROTOTYPE` -- bind(cat_vec, prop_vec) bundled (Cell 1 ARM_FEATURE exact); cross-cell rail anchor with PRIVILEGED cat_vec ground-truth access; expected 0.47 mean (Cell 1 reference)
- `ARM_LINEAR_MEAN_PROTOTYPE` -- bind(mean(instances_c), prop_c) bundled (Cell 1 ARM_CAPABILITY equivalent); the FAIR comparator for Modern Hopfield (both extract from instances only); expected 0.29 mean (Cell 1 reference)
- `ARM_MODERN_HOPFIELD_PROTOTYPE` -- iterative attractor over instances at beta=2.0 (sqrt(D)-scaled effective beta ~181); fixed-point prototype, then bind
- `ARM_MODERN_HOPFIELD_CONTINUOUS` -- Ramsauer single-step softmax: X.T @ softmax(beta * X @ x_mean) at beta=2.0

The MH-vs-LIN_MEAN comparison is the LOAD-BEARING fairness test (both extract from instances, differ only in linear vs non-linear basin). HRR_BUNDLE is retained as the cross-cell-rail anchor (verifies methodology parity with Cell 1) but is not the lift target -- it has unfair access to cat_vec ground truth.

## Pre-registered bands

**HARD_PASS_CHAIN_GRADE_MODERN_HOPFIELD:**
- best_MH_arm mean_heldout_top1 >= 0.65 AND
- best_MH_arm / LIN_MEAN >= 1.35x AND
- HRR_BUNDLE_PROTOTYPE within 0.03 of Cell 1 ARM_FEATURE_BASED_SCHEMA 0.4733 (cross-cell rail OK)

**MIDDLE_BAND [0.50, 0.65]:** best_MH_arm in this range; queue beta-sweep follow-up

**HARD_FAIL_MH_DOESNT_ESCAPE_LINEAR_MEAN_CEILING:** both MH arms within 0.05 of LIN_MEAN (attractor-compression does not escape linear-mean ceiling at this regime; pivot to CLS-replay rank-2 anchor)

**HARD_FAIL_HARNESS_CONFOUND:** ARM_HRR_BUNDLE_PROTOTYPE drifts > 0.03 from Cell 1 reference 0.4733 (3-seed mean). Smoke-mode parity check: seed=11 alone must match Cell 1 seed=11=0.58 within 0.03.

## Cross-cell rail

- `ARM_HRR_BUNDLE_PROTOTYPE` 3-seed mean MUST match Cell 1 ARM_FEATURE_BASED_SCHEMA = 0.4733 within tol=0.03
- Smoke (single seed 11): ARM_HRR_BUNDLE_PROTOTYPE == 0.58 within tol=0.03 (Cell 1 seed-11 exact)
- Same task design as Cell 1: N=8192, 5 cats, 20 train + 10 heldout/cat, CATEGORY_SIGNAL_FRAC=0.005, chance=0.20

Asserted at module init via assert chain; load-bearing for cross-cell interpretation.

## Calibration rationale

P_solve_deflated=0.45 (raw lit P=0.70; -0.20 lit-scan calibration; -0.05 prior modern_hopfield_xl prior collapse memory). The prior `modern_hopfield_xl` HARD_FAIL was a by-construction-saturation issue (both classical and modern at 1.000 above capacity bound) not a beta-collapse; that pattern does NOT apply to this schema-generalization cell (different metric, different task).

Smoke pre-flight signal (seed=11 only, N=8192):
- BASELINE=0.4200, HRR_BUNDLE=0.5800 (rail OK), LIN_MEAN=0.4200, MH_PROTO=0.2200, MH_CONT=0.2600
- Pre-flight WARN: MH arms below LIN_MEAN baseline at beta=2.0. This is the kind of honest negative signal smoke-gate exists for. The 3-seed FULL run is the actual discriminator; if the pattern holds across seeds [11, 13, 19] the verdict is HARD_FAIL_MH_DOESNT_ESCAPE_LINEAR_MEAN_CEILING -- which is itself a chain-grade-eligible negative result that closes the attractor-compression angle and routes Research to CLS-replay (rank-2 anchor).

Information-theoretic intuition for likely-HARD_FAIL: CATEGORY_SIGNAL_FRAC=0.005 means instances are 99.5% noise, 0.5% category-signal. Softmax-beta-weighted aggregation over near-uniform-similar instances adds rather than reduces noise; the mean is the optimal aggregator in this signal-poor regime. The Modern Hopfield ceiling-escape requires a regime where the basin is structurally well-defined (high SNR instances around a clear category center). Substrate's current synthetic-task regime may be below that threshold.

## N-suffix section

Anchor name omits _n8192 suffix per PROT-018 (cell's production N=8192 is canonical for the compositional-gen primitive class; matches Cell 1 ARM-naming exactly). Both smoke and FULL use identical N=8192 per META_M7 capacity-sensitive dim rule. Only SEEDS differ between smoke and full.

## Timeout estimate

Cell 1 elapsed_s = 0.43 for 3 seeds at N=8192. Modern Hopfield adds (per seed):
- iterative-attractor: ~8 steps * 5 cats * (K=20) * D=8192 matmul ~= 8M flops/cat = trivial vs FFT-bind work
- continuous: 1 step * 5 cats * 20 * 8192 = ~1M flops/cat = trivial
- additional linear-mean arm: 5 cats * 20 * 8192 = trivial

Estimated FULL wall: ~1-2s (Cell 1 wall + ~3x for added arms + Modern Hopfield overhead). Plus self-test ~0.1s.

timeout_s = 300 (5 min cap; trivially fits; safety margin 100x).

## Smoke gate verdict

PASS. Cross-cell seed=11 rail HONORED (HRR_BUNDLE=0.58 == Cell 1 seed=11). Baseline matches (0.42 == Cell 1 seed=11). Pre-flight detects MH below LIN_MEAN -- HONEST signal to route. Dispatch to allow full-grid discriminator + Skunkworks cert.

## Disciplines

- ASCII only [PASS]
- Substrate-only at inference; zero LLM forward calls [PASS]
- N=8192 minimum [PASS]
- Per-arm metrics MANDATORY per Fix #28; verdict reads metrics.json per-arm [PASS]
- META_M7 capacity-sensitive dims identical smoke/full [PASS]
- BIAS-Q saturation guard (any arm >= 0.995 cv=0 flag) [PASS via saturation_flags]
- Per-seed checkpoint (PROT-021) [PASS via _seed_checkpoint helpers]
- Pre-reg bands LOCKED via assert chain at module init [PASS]
- Cross-cell rail check (HRR_BUNDLE_PROTOTYPE replicates Cell 1 0.47 within 0.03) [encoded]
- Fix #26 predispatch_check.py = PROCEED (no prior anchor landings)
- 3-arm spread discriminator check encoded in T6 self-test
- Honest smoke pre-flight surfaced expected HARD_FAIL pattern; dispatching for measurable verdict

## Substrate-mining

- Read iterative_attractor.py (existing softmax-beta primitive)
- Read prior modern_hopfield_xl/_v7 metrics: HARD_FAIL was by-construction-saturation (both arms at 1.000), NOT beta-collapse; lesson does not apply here
- Read Cell 1 source + metrics (seeds [11,13,19] => [0.58, 0.40, 0.44] for ARM_FEATURE = 0.4733 mean)
- beta_prototype=2.0 chosen to be sharper-than-uniform but below argmax-collapse regime (effective beta = 2.0*sqrt(8192) = ~181)
