# Pre-registration: substrate_refuse_gate_near_domain_v2

**Date:** 2026-06-25
**Anchor:** substrate_refuse_gate_near_domain_v2
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [11, 13, 19], **V_C_IN:** 600 (200 per in-domain category)

## Strategic intent — closure of refuse-gate partial-tier

V1 (`substrate_refuse_gate_domain_aware_v1`) landed MIDDLE_BAND with ALL three
arms hitting ~1.000 F1. Root cause: query corpus had ZERO surface overlap
between in-domain (animals/geography/tools) and out-of-domain
(medical/legal/financial). Audit primitive never had to discriminate the
near-domain ambiguity that the actual medqa refuse-gate failure produces.
The diagnostic flag `MEDQA_FAILURE_REPRODUCED` never fired, confirming the
test was too easy.

V2 fixes the corpus to stress the real failure mode: queries that use
IN-DOMAIN subjects with OUT-OF-DOMAIN relations. Such queries cause naive
audit (subject-only library-presence check) to false-positive on subject
existence and answer wrong — the actual medqa-style failure.

## Scientific question

Two-part:
1. Does NEAR_DOMAIN_MIXED corpus reproduce the audit-only failure mode that
   the actual medqa refuse-gate cell hit?
2. Given a reproduced failure mode, which fix path closes it:
   - smarter audit alone (subject + relation library-presence check), OR
   - audit + intent composition (naive audit covered by intent classifier)?

## Corpus design (3 categories x 100 queries x 3 seeds)

Substrate loaded ONLY with in-domain facts (V_C_IN=600 concept atoms;
animals/geography/tools; in-domain relations IS_A, HAS_COLOR, USED_FOR).

Test queries split into 3 categories:

1. **PURE_IN_DOMAIN** (100 queries): subject IN-DOMAIN + relation IN-DOMAIN.
   Expected: ANSWER.
2. **PURE_OUT_OF_DOMAIN** (100 queries): subject OUT-OF-DOMAIN + relation
   OUT-OF-DOMAIN (both NOT in substrate). Expected: REFUSE.
3. **NEAR_DOMAIN_MIXED** (100 queries): subject IN-DOMAIN + relation
   OUT-OF-DOMAIN (subject IS in substrate; relation is NOT).
   Expected: REFUSE. **This is the medqa-failure-reproducer.**

Synthesis: queries are `(subject_atom, relation_atom)` tuples bound via
substrate primitive (circular convolution / bipolar binding). NEAR_DOMAIN_MIXED
uses real in-domain subject atoms paired with synthetic out-of-domain relation
atoms (relation names absent from substrate W; relation atoms exist as fresh
bipolar vectors that are NOT in any library matrix the audit consults).

## Arms (4)

### ARM_AUDIT_NAIVE_ALONE
Refuse iff cleanup of `query_subject` against W_subjects returns
best_sim < SUBJECT_AUDIT_THR. Subject-only check (the original audit primitive
shape).

### ARM_AUDIT_RELATION_CHECK
Refuse iff cleanup of `query_subject` OR cleanup of `query_relation` returns
best_sim < threshold (BOTH subject AND relation must be present as atoms).
This is the "smarter audit alone" hypothesis.

### ARM_INTENT_ALONE
Intent classifier scores query.relation against in-domain relation prototypes;
refuses iff confidence < INTENT_CONF_THR (0.03; same as v1).

### ARM_AUDIT_NAIVE_PLUS_INTENT
Refuse iff EITHER naive audit fails OR intent classifier fails.
This is the v1 composition arm; tests whether composition rescues naive audit
even when the smarter audit alone also works.

## Pre-registered bands (LOCKED at module init via assert)

### Sanity rails (must hold on PURE categories across all 4 arms)
- PURE_IN_DOMAIN answer-rate >= 0.85 (any arm refusing too much is broken)
- PURE_OUT_OF_DOMAIN refuse-rate >= 0.85 (any arm answering too much is broken)

### Discrimination on NEAR_DOMAIN_MIXED (the actual test)

**MEDQA_FAILURE_REPRODUCED** (diagnostic; required for test validity):
- AUDIT_NAIVE_ALONE refuse-rate on NEAR_DOMAIN_MIXED < 0.50
  (audit answers when it shouldn't — the failure we wanted to reproduce)

**HARD_PASS_AUDIT_DESIGN_FIX:**
- AUDIT_RELATION_CHECK refuse-rate on NEAR_DOMAIN_MIXED >= 0.70
  (smarter audit fixes the problem; no composition needed)

**HARD_PASS_COMPOSITION_NEEDED:**
- AUDIT_RELATION_CHECK fails (<0.50) BUT AUDIT_NAIVE_PLUS_INTENT >= 0.70
  (composition is genuinely necessary for substrate-product refuse-gate)

**HARD_PASS_BOTH_WORK:**
- BOTH AUDIT_RELATION_CHECK >= 0.70 AND AUDIT_NAIVE_PLUS_INTENT >= 0.70
  (multiple paths close it; pick the simpler — audit-relation-check)

**HARD_FAIL_REFUSE_GATE_DEEP:**
- AUDIT_NAIVE_PLUS_INTENT < 0.50 on NEAR_DOMAIN_MIXED
  (composition doesn't help; refuse-gate has deeper problem)

**TEST_DESIGN_FAILED:**
- MEDQA_FAILURE_REPRODUCED does NOT fire (AUDIT_NAIVE_ALONE refuses
  correctly anyway; test still too easy — synthesis didn't create real
  surface-mismatch)

### Discipline rails
- cv <= 0.07 across 3 seeds (F1 / refuse-rates on NEAR_DOMAIN_MIXED for any arm)
- PURE_IN_DOMAIN answer-rate cv <= 0.05

## Strategic significance

Three outcomes close partial-tier audit capability:

1. **AUDIT_RELATION_CHECK fixes it alone:** audit primitive evolves to do
   subject+relation library-presence check; no architectural composition
   needed. Close partial-tier as "audit primitive design improvement."
2. **Only composition works:** audit + intent composition becomes the
   substrate-product refuse-gate primitive. First Stage-3 application
   composition proven definitively.
3. **Nothing works:** refuse-gate has deeper problem; substrate-product audit
   is limited to clear-cut deletion/paraphrase/hallucination cases. Honest
   negative; close partial-tier as "audit primitive limitation."

ALL THREE outcomes close the gap.

## Calibration rationale

- **0.70 NEAR_DOMAIN_MIXED refuse threshold:** lower than 0.85 sanity rail
  because NEAR_DOMAIN_MIXED is the hardest discriminating category and a 70%
  refuse-rate represents a meaningful improvement over the audit-naive
  baseline (expected <50% by the MEDQA_FAILURE_REPRODUCED diagnostic).
- **0.50 MEDQA_FAILURE_REPRODUCED threshold:** below 50% refuse-rate means
  audit_naive answered most of these — a real failure-mode reproduction.
- **0.85 PURE answer/refuse-rate sanity rails:** match deployed-product
  responsiveness/safety floors used in v1.
- **cv <= 0.07 across 3 seeds:** standard substrate-stability requirement
  for deterministic per-seed runs.

## Q-discipline (BIAS-Q: suspect 1.000 results) — Hardened from v1

If any single-arm refuse-rate on NEAR_DOMAIN_MIXED hits >= 0.995, treat as
suspect saturation; verify:
1. NEAR_DOMAIN_MIXED subject atoms have audit_sim >= 0.95 against substrate
   library (confirming the subject IS detectable as in-substrate).
2. NEAR_DOMAIN_MIXED relation atoms have audit_sim < 0.20 against substrate
   relation library (confirming the relation IS NOT detectable).
3. Without (1) and (2), NEAR_DOMAIN_MIXED isn't actually testing
   surface-mismatch and the 0.995 number is meaningless. Smoke self-test
   asserts (1) and (2) before any FULL dispatch.

## Capacity-feasibility analysis

- V_C_IN = 600 in-domain concept atoms at N=8192. Capacity headroom for
  cleanup over 600-atom codebook is sqrt(8192/600) = 3.7. Well above floor.
- N_DOMAINS = 6 category prototypes; signal-to-noise high (1/sqrt(8192) = 0.011).
- 8 in-domain relations + 8 out-of-domain relations at N=8192; fully resolvable.
- Capacity feasible at this regime.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix (mechanism cell at N=8192 only).
PROT-018 does not apply.

## Timeout estimate

V1 ran at N=8192, 3 seeds, 200 queries in 1.1s total wall (matrix-vector
ops, sub-1s per seed). V2 adds a second matrix and a relation library; ~2x
compute. Smoke at smoke N=2048, 1 seed, 20 queries-per-category ~ 1-2s.

formula: timeout_s = ceil(1.5 * 5 * (8192/2048)^1.5 * (3*300/(1*60))) =
ceil(1.5 * 5 * 8 * 15) = 900s. Round up to 1800s as conservative budget;
expected wall ~5-10s.

Budget: **timeout_s = 1800** (30 min).

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH directions per arm:
- PURE_IN_DOMAIN answer-rate (responsiveness)
- PURE_OUT_OF_DOMAIN refuse-rate (safety)
- NEAR_DOMAIN_MIXED refuse-rate (the actual closure metric)
- F1 (refuse-class) per category
- All four arms reported with full per-category metrics; no aggregate-only.

## Composition substrate parts

- Substrate library W_subjects: V_C_IN bipolar concept atoms at N=8192.
- Substrate library W_relations_in: V_relations_in=8 in-domain relation atoms.
- Intent classifier: per-category prototypes (from a1_substrate_intent_classifier_v1
  pattern); operates on relation-shaped queries.
- Audit primitive (naive variant): cosine cleanup-style library-presence
  check against W_subjects only.
- Audit primitive (relation-check variant): library-presence check against
  W_subjects AND W_relations_in.
