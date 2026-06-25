# Pre-registration: substrate_refuse_gate_domain_aware_v1

**Date:** 2026-06-25
**Anchor:** substrate_refuse_gate_domain_aware_v1
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [11, 13, 19], **V_C_IN:** 600 (200 per in-domain category)

## Strategic intent

Close partial-tier audit capability for domain-specialized refuse via
audit + intent classifier composition.

Existing diagnostics:
- AUDIT primitive: chain-grade for "this isn't in our library"
  (`exp_kinetic_proofreading_refuse_envelope_smoke_v1` HARD_PASS).
- INTENT classifier: chain-grade for domain classification
  (`exp_a1_substrate_intent_classifier_v1` chain-grade-eligible).
- medqa refuse-gate: HARD_FAIL (audit alone can't do domain reasoning).

This cell asks: does composing the two primitives close the medqa-style
domain-aware refuse failure? Each primitive does ONE job well; never asks
audit to do domain reasoning OR asks intent to do library-presence checks.

## Scientific question

Does composing intent classifier (domain detector) with audit primitive
(library-presence detector) achieve domain-aware refuse-gate behavior that
EITHER single primitive cannot?

## Pre-registered bands

**HARD_PASS_CHAIN_GRADE_COMPOSITION:**
- in-domain answer-rate >= 0.85 in COMPOSED arm
- out-of-domain refuse-rate >= 0.85 in COMPOSED arm
- composed arm F1 > BOTH AUDIT_ALONE F1 AND INTENT_ALONE F1
  (composed lift >= 0.02 over each single primitive)
- cv <= 0.07 across seeds (composed arm F1)

**HARD_PASS_PARTIAL:**
- composed arm F1 > both single-primitive F1s by >= 0.02 but rate < 0.85

**MIDDLE_BAND:**
- composed arm ties best single-primitive arm (F1 within +/- 0.02)

**HARD_FAIL_COMPOSITION_DOESNT_HELP:**
- composed arm strictly WORSE than best single primitive (F1)

**MEDQA_FAILURE_REPRODUCED (diagnostic; orthogonal to HP/HF):**
- AUDIT_ALONE out-of-domain refuse-rate < 0.50
  (confirms existing medqa REFUTED finding; expected diagnostic outcome)

## Calibration rationale

- 0.85/0.85 chain-grade thresholds: deployed refuse-gate must be both
  responsive (answers most in-domain queries) AND safe (refuses most
  out-of-domain queries). Below 0.85 either side, the gate fails the
  deployed-product threshold.
- F1 lift >= 0.02: per Skunkworks discipline; sub-0.02 differences are
  noise at n_queries=100 per domain.
- cv <= 0.07 across 3 seeds: substrate is deterministic per-seed; >7%
  variability indicates seed-dependent synthesis bias.
- MEDQA_FAILURE_REPRODUCED diagnostic threshold 0.50: confirms the
  pre-existing audit-only failure mode the composition is meant to fix.

## Q-discipline (BIAS-Q: suspect 1.000 results)

If composed arm scores >= 0.995 in_answer_rate AND >= 0.995 out_refuse_rate
simultaneously, treat as suspect; verify:
1. out-of-domain queries are NOT accidentally near in-domain library atoms
   (synthesis bug);
2. intent classifier confidence threshold is not gaming the test (e.g.,
   refusing everything below confidence trivially gets out-refuse-rate near
   1.0 by penalizing in-domain). Honest expectation: composed F1 in [0.70,
   0.95] range, with both arms in [0.55, 0.85] range.

## Capacity-feasibility analysis

- V_C_IN = 600 in-domain concept atoms at N=8192. Capacity headroom for
  cleanup over 600-atom codebook is sqrt(8192/600) = 3.7. Well above the
  ~1.0 capacity-feasibility floor.
- N_DOMAINS = 6 category prototypes. Cosine prototype-vs-noise floor
  ~sqrt(1/8192) = 0.011; signal-to-noise for 50%+50%-mix queries is very
  high.
- AUDIT_MATCH_THRESHOLD = 0.50 (cosine sim threshold). Out-of-domain atoms
  built as 50% prototype + 50% random; max cosine to any in-domain atom
  should be << 0.50 unless prototype alignment leaks.

Capacity feasible at this regime.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix (mechanism cell at N=8192 only).
PROT-018 does not apply.

## Timeout estimate

Smoke ~ 5-10s estimated at N=2048, 1 seed, 20 queries.
FULL: N=8192, 3 seeds, 200 queries (100 in + 100 out).
Scaling: per-query matmul; scaling_exp = 1.5 (matrix-vector + cleanup).
formula: ceil(1.5 * 5 * (8192/2048)^1.5 * (3*200/(1*20))) = ceil(1.5 * 5 * 8 * 30) = 1800s
Budget: timeout_s = 1800 (30 min). Conservative; expected wall ~5-15 min.

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Compute and report BOTH directions:
- in-domain answer-rate (responsiveness)
- out-of-domain refuse-rate (safety)
- F1 treating "correctly refused out-of-domain query" as positive class
- composed-vs-best-single lift (with signed direction)

No one-sided framing in verdict_msg.

## Composition substrate parts

- Substrate library: Hebbian-bound concept-to-category-prototype W at N=8192.
- Intent classifier: per `a1_substrate_intent_classifier_v1`'s Hebbian
  Hd-bound classifier pattern; uses category prototypes + cosine argmax.
- Audit primitive: cosine cleanup-style library-presence check
  (chain-grade pattern from kinetic-proofreading refuse-envelope smoke).
