# Pre-registration: substrate_cortical_schema_extraction_compositional_generalization_v1

**Date:** 2026-06-25
**Anchor name:** substrate_cortical_schema_extraction_compositional_generalization_v1
**Script:** experiments/exp_substrate_cortical_schema_extraction_compositional_generalization_v1.py
**Queue:** local_cpu_queue
**Authority:** USER directive 2026-06-25 ("build the 3 missing brain-consolidation primitives. Full auto. NREM replay -> synaptic homeostasis -> cortical schema-extraction")
**Composes with:** substrate_continual_NREM_replay_v1 (pillar 1); substrate_synaptic_homeostasis_global_downscale_v1 (pillar 2); substrate_native_capability_suite_shotgun_v1 ARM_COMPOSITIONAL_GEN (baseline 0.00 heldout that this cell aims to lift); distill_verify_v4 (substrate self-discovered corpus mechanism)
**Brain pillar:** 3 of 3 (cortical schema extraction; bridges Gap 3 + Gap 4)

---

## Scientific question

Cortex extracts shared structure from hippocampal episodes into semantic schemas.
Schemas compose with NOVEL instances at the right abstraction level. Substrate capability
suite ARM_COMPOSITIONAL_GEN scored 0.00 heldout on subj-obj composition: substrate has
NO schema layer today.

Substrate analog: periodic batch scan finds clusters of atoms sharing a category feature,
extracts a SCHEMA atom (per-cat prototype bound to property). Query time: novel instance
unbinds schema-bundle to recover property via cat-signal in instance vector.

Question: does HRR schema extraction enable compositional generalization to novel instances?

## Pre-registered bands (LOCKED via module-init assert)

Brain-realistic compositional-gen test: schema mechanism must beat episodic
nearest-neighbor baseline by a discriminating margin (cortex > hippocampus).

| Band | Condition |
|------|-----------|
| HARD_PASS_SCHEMA_ENABLES_COMPOSITIONAL_GEN | COMBINED_SCHEMAS >= 0.50 AND lift_over_baseline >= 0.15 AND cv <= 0.07 |
| HARD_PASS_PARTIAL_SCHEMA_LIFTS_COMPOSITIONAL | COMBINED >= 0.30 AND lift_over_baseline >= 0.10 |
| MIDDLE_BAND_PARTIAL_SIGNAL | max_schema_lift >= 0.05 but COMBINED insufficient |
| HARD_FAIL_SCHEMA_DOESNT_HELP | max_schema_lift <= 0.02 (all schema arms match baseline within tol) |

Sacrosanct both ways. Chance = 1/5 = 0.20.

## Arms (4)

| Arm | Mechanism |
|-----|-----------|
| ARM_NO_SCHEMA_BASELINE | nearest-neighbor lookup in training atoms; predict its category's property |
| ARM_CAPABILITY_BASED_SCHEMA | bundle = sum_c bind(prototype_c, prop_c); prototype = mean training instance |
| ARM_FEATURE_BASED_SCHEMA | bundle = sum_c bind(cat_vec_c, prop_c); typed-signature given cat-tag |
| ARM_COMBINED_SCHEMAS | bundle(cap) + bundle(feat); both mechanisms aggregated |

Query time: substrate has ONLY the heldout instance vector (NO cat tag). Unbinds the
schema-bundle by the instance; cleanup against prop bank picks top1.

## Config (FULL)

- N = 8192
- N_CATEGORIES = 5; INSTANCES_PER_CATEGORY = 20; HELDOUT_PER_CATEGORY = 10 -> 50 heldout
- CATEGORY_SIGNAL_FRAC = 0.005 (instance variance carried by cat-vec; discriminating regime
  per N=8192 sweep: NN baseline ~0.30, schema bundles 0.30-0.50)
- 3 seeds [11, 13, 19]
- Substrate-only (HRR circular convolution via FFT; bind = ifft(fft*fft); unbind = exact
  FFT division with epsilon regularization). Zero LLM forward calls.

## Self-tests (4 formula + bands lock)

1. HRR bind/unbind roundtrip via exact FFT division: cosine = 1.0 at N=8192
2. Schema composition: bind(cat, prop) then unbind by cat -> prop cosine = 1.0
3. No-schema baseline non-NaN at small N with cat-signal
4. Bands locked at module init

## Smoke result (script-validity gate; 2026-06-25)

- N=2048, sig_frac=0.005, 1 seed, 4 arms; wall ~0.07s
- VERDICT: HARD_FAIL_SCHEMA_DOESNT_HELP at smoke regime (NO_SCHEMA=0.38, schemas
  0.22-0.26; schemas score WORSE than baseline at smoke N).
- This is an HONEST signal at smoke N=2048: HRR superposition crosstalk dominates with
  only 2048 dimensions and 5 cat-prop bindings.
- At full N=8192 (per earlier sweep): NN=0.40, feat=0.42, comb=0.38 -> still close to
  HARD_FAIL territory. The cell as designed may HARD_FAIL at full scale too.
- Honest preview: substrate's HRR-based schema mechanism may not be sufficient at this
  scale. HARD_FAIL would be a legitimate result informing Gap 3 stays open and a different
  schema mechanism (e.g., learned projection, prototype attractor) is needed.
- Script + bands operational; full run provides the actual scientific verdict.

## Honest scope

Cortical schema extraction via HRR bundle of cat-prop bindings; 5-way compositional
classification on novel instances; substrate-only (no LLM, no learned weights). The
test is whether the HRR-aggregation mechanism extracts category structure from
training-instance prototypes well enough to enable property recovery on novel instances
via instance-key unbinding.

DOES NOT show: deeper schema hierarchies, transitive composition, brain-grain
hippocampus-cortex transfer dynamics.

## Q-discipline saturation guard

If any arm has cv=0.0000 AND heldout_top1=1.0000 with baseline > 0.20, flag as
by-construction-saturation (the design leaked category into the test). Skunkworks tiers.

## Strategic significance

- HARD_PASS: substrate gains first compositional-gen primitive; closes Gap 3
- HARD_FAIL: honest negative; substrate-HRR schema mechanism insufficient at this scale;
  informs that a DIFFERENT mechanism (learned attractor, exact lookup table, attention)
  is needed for compositional generalization
- MIDDLE_BAND: schemas provide measurable but insufficient lift; informs which arm
  mechanism (capability vs feature) is the bridgeable path
