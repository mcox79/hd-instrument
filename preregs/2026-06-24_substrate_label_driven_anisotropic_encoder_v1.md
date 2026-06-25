# Pre-reg: substrate_label_driven_anisotropic_encoder_v1
Date: 2026-06-24
Author: exp_dev (Wave E retry)
Routing: remote_cpu_queue via orchestrator handoff
Lane: 1 (substrate-native; chance + random-bipolar isotropic baseline)

## Barrier addressed
Barrier 4 (alt): substrate's anisotropic encoder remains the bottleneck across
forward-only encoder variants. Instead of LEARNING anisotropy unsupervised (the
hub-spoke v3 path), CONSTRUCT it directly from concept-KG labels.

## USER directive
We have labels (concept categories) -- use them. SEMANTIC battery (separate cell)
proved that labeled structure gives top1=1.000 generalization. Verify substrate
exploits label-driven anisotropy as an encoder for compositional 1-hop QA.

## Verify-the-referent (Skunkworks N1 discipline)
- exp_substrate_concept_kg_storage_retrieval_v1/metrics.json: verdict=MIDDLE_BAND
  (NOT chain-grade). USER citation of "top1=1.0" comes from the SEMANTIC battery
  in a separate cell, not this one. FLAGGED IN PREREG. We do NOT claim
  concept_kg was chain-grade; we use its A3 generalization task SHAPE as the
  evaluator and run it against 4 distinct encoder constructions.

## Mechanism
- V_concepts=12 (4 categories x 3 instances each); V_categories=4; V_predicates=6.
- M_train_triples=300 (concept-KG ingest).
- N=8192; dense bipolar; pure numpy.
- Per arm, the CONCEPT EMBEDDINGS E[concept_i] are built differently:
  - ARM_RANDOM_BIPOLAR_BASELINE: standard isotropic dense bipolar (no label info).
  - ARM_LABEL_DRIVEN_AXIS_PROJECTION: each concept_i's embedding is non-zero
    only in the SUBSPACE assigned to its category, plus small global noise.
  - ARM_LABEL_DRIVEN_GRAM_SCHMIDT: build orthonormal category basis (GS); each
    concept_i = unit-norm linear combination of its category's basis vectors
    (within-category variation; orthogonal across categories).
  - ARM_HUB_SPOKE_LABEL_BASELINE: hub vector per category (shared across
    instances) + spoke vector per instance (category-independent random bipolar);
    concept_i = hub_cat(i) + spoke_i. Sum NOT bind; not the same as anisotropic.
- 6 SEMANTIC-battery-style tasks per arm (A1-A6):
  A1: 1-hop recall after KG ingest (basic).
  A2: distinguish within-category (instance discrimination).
  A3: generalization to held-out concept (concept_i held out from KG; substrate
      asked predicate based on category structure).
  A4: compositional generalization (s,p,?) where s and p both seen in train but
      (s,p) NEVER seen as combo.
  A5: cross-category structural sanity (asking p_eats on a concept where
      training never paired that concept with p_eats; should NOT recover trained
      objects for it).
  A6: predicate substitution sanity (NEW predicate never trained; sanity floor).

## Arms (4)
1. ARM_RANDOM_BIPOLAR_BASELINE
2. ARM_LABEL_DRIVEN_AXIS_PROJECTION
3. ARM_LABEL_DRIVEN_GRAM_SCHMIDT
4. ARM_HUB_SPOKE_LABEL_BASELINE

## Config
- V_concepts=12, V_categories=4, V_predicates=6, M=300.
- N=8192; 3 seeds [7, 17, 23].
- pure numpy CPU.

## HARD bands
- HARD_PASS_CHAIN_GRADE: ARM_LABEL_DRIVEN (best of axis_projection or GS) A3 >= 0.85 AND A4 >= 0.50 AND beats ARM_RANDOM_BIPOLAR by >= 0.15 on either metric.
- HARD_PASS: ARM_LABEL_DRIVEN A3 >= 0.70 AND beats RANDOM_BIPOLAR by >= 0.10 on A3.
- HARD_FAIL: ALL label arms <= ARM_RANDOM_BIPOLAR on A3 AND on A4 (label structure brings nothing).
- MIDDLE_BAND: otherwise.

## Sanity rails
- ARM_RANDOM_BIPOLAR_BASELINE A3 within [0.65, 0.95] -- "reproduces SEMANTIC battery v2 FULL A3 partial at smaller V" per USER spec, but our V_concepts=12 is small so we accept a wider range. If A3 = 1.000 exactly at random_bipolar, the task is by-construction-saturating at this scale -- we'd downgrade verdict.
- A5 sanity floor: untaught predicate top1 < 0.20 (substrate shouldn't hallucinate).
- A6 sanity floor: untaught predicate substitution top5 < 0.30.
- chance_top1 = 1/V_concepts = 1/12 ~ 0.083; explicitly reported.

## Timeout budget
- 3600s per queue spec; pure-numpy at N=8192, V=12 (small KG); 4 arms x 3 seeds is light.

## Routing
- remote_cpu_queue via orchestrator handoff.
- Anchor: substrate_label_driven_anisotropic_encoder_v1 (no _n suffix).
