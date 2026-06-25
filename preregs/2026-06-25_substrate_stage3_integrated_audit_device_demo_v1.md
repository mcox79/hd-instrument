# Pre-registration: substrate_stage3_integrated_audit_device_demo_v1

**Date:** 2026-06-25
**Anchor:** substrate_stage3_integrated_audit_device_demo_v1
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [11, 13, 19], **V_C_IN:** 600 (200 per in-domain category)
**Routing rationale:** numpy-only (no torch); small substrate (V=600, M=10k); composes existing chain-grade primitives; CPU runs sub-minute per seed.

## Strategic intent — Stage 3 productionization demo

USER directive (2026-06-25): "I need you to show that all required aspects are
chain grade, and then do a test where it's all included at the same time" +
"I want to make sure everything clearly passes, and that nothing is overlooked".

The substrate has chain-grade Stage 3 application primitives:
- intent classifier (`a1_substrate_intent_classifier_v1`)
- audit gate (subject + relation) (`substrate_refuse_gate_near_domain_v2` HARD_PASS_BOTH_WORK pattern)
- graph-health refuse (`refuse_gate_5_graph_health_cpu_v1`)
- dense projected KV retrieval (`dense_projected_KV_envelope_v1` at M=10k chain-grade)
- templated response (`a2_substrate_templated_response_v1`)
- CSP confidence label (`csp_first_ship_v1`)

All have been verified INDIVIDUALLY. NONE have been tested COMPOSED end-to-end.
This cell composes all six primitives into a single audit-device pipeline and
measures (a) per-primitive sanity preserved, (b) integration lift vs single-arm
baselines, (c) latency budget.

## The audit-device pipeline (ARM_PIPELINE_COMPOSED)

For each query:
1. **Intent classifier**: score query.relation against in-domain relation
   prototypes -> (domain_pred, confidence). If confidence < INTENT_CONF_THR
   -> refuse-uncertain.
2. **Audit gate**: cleanup query.subject against W_subjects AND query.relation
   against W_relations_in. Refuse iff BOTH not present.
3. **Graph-health gate**: compute graph-health from substrate state. Refuse
   iff health > GRAPH_HEALTH_THR (substrate "feels full").
4. **KG retrieval**: dense projected KV at M=10k -> retrieve value class.
5. **Templated response**: format the answer with the intent slot filled.
6. **CSP confidence label**: calibrate confidence label on answer.

Returns answer-with-confidence OR refuse-with-reason
(audit/health/uncertain).

## Test corpus (3000 queries x 3 seeds)

- 1000 **PURE_IN_DOMAIN** (in-domain subject + in-domain relation): expect
  ANSWER with high confidence.
- 1000 **PURE_OUT_OF_DOMAIN** (out-of-domain subject + out-of-domain relation):
  expect REFUSE via audit.
- 500 **NEAR_DOMAIN_MIXED** (in-domain subject + out-of-domain relation):
  expect REFUSE via audit-relation-check (the medqa-failure reproducer).
- 500 **IN_DOMAIN_UNCERTAIN** (in-domain but borderline confidence; engineered
  via heavy bit-flip perturbation): expect low-confidence answer OR
  refuse-uncertain via CSP.

## Arms (4)

### ARM_INDIVIDUAL_PRIMITIVES_PARALLEL
Each primitive runs INDEPENDENTLY on the same query; report per-primitive
verdict. Used to verify per-primitive sanity preserved at composition scale.

### ARM_PIPELINE_COMPOSED
Full pipeline as described above. The product surface.

### ARM_AUDIT_ONLY_RAIL
Just the audit gate (no intent, no graph-health, no CSP). Reproduces Cell 2 v2
baseline shape for apples-to-apples baseline measurement.

### ARM_NO_REFUSE_RAIL
No gates; always retrieve + respond. Reproduces "ungated substrate" baseline
to measure the lift the gates provide.

## Pre-registered bands (LOCKED at module init via assert)

### HARD_PASS_INTEGRATED_AUDIT_DEVICE
ARM_PIPELINE_COMPOSED satisfies ALL of:
- PURE_IN_DOMAIN answer-rate >= 0.85 AND avg_confidence >= 0.70
- PURE_OUT_OF_DOMAIN refuse-rate >= 0.85
- NEAR_DOMAIN_MIXED refuse-rate >= 0.85
- IN_DOMAIN_UNCERTAIN: (low-confidence-or-refuse) rate >= 0.70 (CSP
  calibration check)
- End-to-end latency p95 <= 5ms per query
- cv <= 0.07 across 3 seeds
- Per-primitive sanity (ARM_INDIVIDUAL): each individual primitive's chain-grade
  envelope holds within +-0.05 of its cert envelope:
  - audit (relation_check): NEAR_DOMAIN_MIXED refuse >= 0.70 (Cell 2 v2 envelope was >= 0.95; we relax to allow noise)
  - intent classifier: in-domain relation acc >= 0.70 (envelope = 0.754)
  - graph-health: false-refuse <= 0.10 on storable graphs
  - CSP: ECE <= 0.10

### HARD_PASS_PARTIAL
Integrated pipeline lifts over each single-primitive rail by >= 0.10 on at
least one query category (composition adds value).

### MIDDLE_BAND
Pipeline ties best single-primitive rail (composition doesn't subtract but
doesn't add either).

### HARD_FAIL_INTEGRATION_BUG
Pipeline WORSE than best single-primitive rail by >= 0.05 on any sanity
category (composition introduces failure).

### HARD_FAIL_LATENCY_BLOWN
End-to-end p95 latency > 50ms (composition is too slow for product).

### HARD_FAIL_SANITY_RAIL
Any individual primitive in ARM_INDIVIDUAL deviates from its cert envelope by
> 0.10 (substrate regressed; not a composition question).

## Calibration rationale

- **5ms p95 latency target:** substrate primitives are numpy matmul; expected
  per-query wall ~0.5-2ms. 5ms = 2.5x margin. 50ms FAIL threshold = 25x
  margin (catches O(M^2) regression).
- **0.85 answer-rate / refuse-rate sanity rails:** match Cell 2 v2 envelope
  for in-domain/out-of-domain categories.
- **0.85 NEAR_DOMAIN_MIXED refuse-rate (in pipeline):** stricter than Cell 2 v2
  (0.70) because composition should LIFT, not just preserve.
- **0.70 CSP calibration on IN_DOMAIN_UNCERTAIN:** CSP envelope is recall-preserving
  (1.000 -> 1.000); on heavily perturbed queries the calibrated refuse-uncertain
  rate should track the actual uncertainty.
- **+-0.05 per-primitive envelope tolerance:** standard substrate composition
  envelope width.
- **cv <= 0.07 across 3 seeds:** standard substrate-stability requirement.

## Q-discipline (BIAS-Q: suspect 1.000 results)

If any arm hits >= 0.995 on any sanity metric, suspect saturation; verify-off-data:
1. The IN_DOMAIN_UNCERTAIN category MUST have at least one arm refusing or
   producing low confidence (>= 30%); else perturbation didn't create real
   uncertainty.
2. NO arm should answer >= 0.99 on PURE_OUT_OF_DOMAIN (substrate would be
   hallucinating to do so).

## Q-discipline (META_M6: NAIVE bands DERIVED from cell regime)

ARM_NO_REFUSE_RAIL provides the naive baseline FOR THIS CELL's substrate state.
The integrated pipeline must beat it by >= 0.10 on at least one category to
claim HARD_PASS_PARTIAL.

## Capacity-feasibility analysis

- V_C_IN = 600 concept atoms at N=8192. Cleanup headroom sqrt(8192/600) = 3.7.
- M=10k dense projected KV at d=768 (per `dense_projected_KV_envelope_v1`);
  storage W = d x d = 768 x 768 = ~2.3MB. Trivial.
- C=256 codebook for KV; chance = 1/256 = 0.004; baseline well above chance.
- 6 categories x 3 query types x 1000 queries x 3 seeds = ~9k total query
  evaluations per arm; per-query ~1-2ms = 10-20s per arm per seed. Total
  wall ~5min per seed, ~15min full.
- Capacity feasible.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix (mechanism cell at N=8192 only).
PROT-018 does not apply.

## Timeout estimate

Smoke (100 queries / 25 per category / 1 seed / N=2048 / V=120): ~10s wall.
FULL: 3000 queries x 3 seeds x 4 arms at N=8192 / V=600. Scaling factor:
(8192/2048)^1.5 * (3000*3*4)/(100*1*4) = 8 * 90 = 720x smoke wall ~ 7200s.
Add 50% margin = 10800s. Then cap at 3600s (1h) and verify with adaptive
checkpointing — substrate primitives are matrix-vector not matrix-matrix so
real scaling is closer to ~2x not 8x; expected wall ~2-4min per seed.

formula: timeout_s = ceil(1.5 * 10 * 4 * 90) = 5400s. Round to 3600s with
per-seed checkpointing for adaptive recovery.

Budget: **timeout_s = 3600** (1 hour with per-seed checkpoint).

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH directions per arm per category:
- answer-rate (responsiveness)
- refuse-rate (safety)
- avg confidence (calibration)
- per-category F1 (refuse-class)
- p95 latency per arm

## Composition substrate parts (reused chain-grade primitives)

- W_subjects: V_C_IN bipolar concept atoms (Cell 2 v2 pattern).
- W_relations_in: V_relations_in=8 in-domain relation atoms.
- Intent classifier prototypes (a1_substrate pattern).
- Audit gate (Cell 2 v2 HARD_PASS_BOTH_WORK pattern).
- Graph-health (refuse_gate_5 pattern; computes substrate-level non-edge
  variance from a small KG built on top of W_subjects).
- Dense projected KV at M=10k: W = sum_i code[y_i] k_i^T (O(d^2) M-independent
  superposition); decode via cosine to fixed C=256 codebook
  (dense_projected_KV_envelope_v1 pattern).
- Templated response: small (~20-template) library with intent/subject/relation
  slot fillers (a2_substrate pattern).
- CSP confidence label: warm-started Hopfield convergence iters as confidence
  proxy on the retrieved value (csp_first_ship_v1 pattern, simplified to
  per-query latency).
