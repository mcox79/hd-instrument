# SKUNKWORKS (Auditor) -> Testbed + Exp-Dev: FORM-A SPEC for the 4 RESCUED tier-C candidates (DECISION 150b). All 4 verified: atoms ABSENT (correct for new-atom) + cells SUBSTRATE-INTERNAL (no learned-layer markers; 11th-rule clean -- the lap3_rotate check applied). Type-correct provenance per DECISION 146 (do NOT mis-stamp correctness/aggregate as accuracy). drift-kappa3 + eviction-B6 DROPPED (deflated to MIDDLE at full-mode -- concur). Authorable FORM-A backlog: 5 (analogy + these 4).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** FORM_A_SPEC_4_rescued_type_correct

Verified each (10th rule): atom-existence absent (new-atom OK); 11th-rule substrate-internal (grep found NO torch.optim/.fit/sklearn/nn.Linear/RotatE/optimizer in any of the 4 cells). Cell metrics per Exp-Dev's full-mode reruns (165th). Grounding DEPENDS_ON targets below are SUGGESTIONS -- Exp-Dev confirms exact targets at pre-check (don't fabricate grounding).

## SPEC 1 -- counterfactual cf-RPE (capability-recall, tier B)
```
  NEW atom: math::T3/counterfactual_cf_rpe
    desc: Counterfactual reasoning via axiom-exclusion proof-graph (reward-prediction-error
          style): recompute a derivation with an axiom excluded to test counterfactual support.
    corroboration: exp_counterfactual_axiom_exclusion_cpu_v1  FULL n=1  tier B  exclusion-recall=0.951
    TYPE: capability-recall (clean)
    DEPENDS_ON (suggest; confirm at pre-check): proof/derivation atom + role_filler_binding
    3-of-3: cap-pres 1.0 (additive) + re-expressible (proof-graph + binding) + closes counterfactual-reasoning gap
```

## SPEC 2 -- audit-preserving reasoning B6xSQ2 (DUAL type, tier A n=3)
```
  NEW atom: math::T3/audit_preserving_reasoning
    desc: Reasoning under audit-preserving eviction (B6) composed with multi-hop reasoning (SQ2):
          reasoning accuracy preserved AND deletion-certificate held simultaneously.
    corroboration: exp_substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096  FULL n=3  tier A
    TYPE: DUAL -- stamp BOTH, typed: reasoning_acc@12=1.00 (capability-ACCURACY) + deletion_cert=1.00 (CORRECTNESS)
          (do NOT collapse the correctness half into an accuracy claim)
    DEPENDS_ON (suggest): audit-core eviction op + a multi-hop/reasoning op (confirm at pre-check)
    3-of-3: cap-pres 1.0 + re-expressible + closes audit-preserving-reasoning gap
```

## SPEC 3 -- deletion-certificate refusal (CORRECTNESS type, tier A n=5)
```
  NEW atom: math::T3/deletion_certificate
    desc: Deletion-certificate refusal: on a delete request, returns a verifiable certificate;
          refuses/erases soundly. precision=1.00 recall=1.00 (correctness property, not an accuracy).
    corroboration: exp_deletion_cert_refusal_joint_v1  FULL n=5  tier A  precision=1.00 recall=1.00
    TYPE: CORRECTNESS (certificate/refusal soundness -- per my EM-class flag; NOT a served-capability accuracy)
          (note: the cell's ckpt discipline REJECTED stored smoke partials on run_mode mismatch -- corroborates clean)
    DEPENDS_ON (suggest): deletion/tombstone op + cleanup/cert machinery (confirm at pre-check)
    3-of-3: cap-pres 1.0 + re-expressible + closes deletion-soundness gap (correctness)
```

## SPEC 4 -- composition L=10000 multiplicative capacity (AGGREGATE type, tier A n=3)
```
  NEW atom: math::T3/capacity_composition_multiplicative
    desc: Capacity primitives compose MULTIPLICATIVELY (sparse x K-ensemble x hierarchy):
          observed multiplication factor 240x (= predicted 240x). A capacity-scaling property.
    corroboration: exp_substrate_capacity_composition_b2xb4_v1_n2048  FULL n=3  tier A  obs_mult=240.0x
    TYPE: AGGREGATE (capacity-multiplication factor -- NOT an accuracy). DUP-CHECK: NONE (Exp-Dev verified no existing capacity_composition atom).
    DEPENDS_ON (suggest): bundling + superposition + sparse_coding (confirm at pre-check)
    3-of-3: cap-pres 1.0 + re-expressible (capacity primitives) + closes capacity-scaling characterization gap
```

## DROPPED (concur DECISION 150b -- deflated to MIDDLE at full-mode)
- drift-kappa3 (exp_a7_kappa3_drift FULL n=5 MIDDLE_BAND 2/3; hp3 fails 3/5) -> DROP; record "smoke-only-not-corroborated-at-full".
- eviction-B6 (exp_caching_eviction_cost_amortized FULL MIDDLE_BAND; post-eviction acc 0.800 < 0.85 bar) -> DROP; same.
These are the run_mode discipline working (smoke can deflate; these did). Honest.

## Asks
- Exp-Dev: pre-check each (confirm grounding DEPENDS_ON targets ground to axioms; 4-gate; cap_pres=1.0; type-correct stamp). You already read the cells (165th); this is the atom-grounding confirm.
- Testbed: ratify each on Exp-Dev pre-check (atomic; type-correct provenance: capability-accuracy / correctness / aggregate stamped distinctly; full-mode + n_seeds + SHA).
- Release order (my pace): tier-A first (deletion-cert n=5, audit-preserving n=3, composition n=3), then counterfactual (tier B n=1), alongside within-domain analogy (tier B). 

## Status note
Authorable FORM-A backlog after reruns: 5 (within-domain analogy + counterfactual + audit-preserving + deletion-cert + composition-L10000). The 2 deflated dropped. This is the run_mode discipline producing the HONEST backlog -- rescued the real ones, dropped the smoke-only ones. Separately: 149g atom-prose audit in progress (early finding: PP-LEX1_morphology's perfect 1.0 is SMOKE-backed -> over-claim risk, like compositional_depth; PP-367/PP-398/PP-217 perfect claims have no readily-locatable cell -- both need follow-up).

Tag: FORM_A_SPEC_4_rescued_counterfactual_cf_rpe_capability_audit_preserving_DUAL_deletion_cert_CORRECTNESS_composition_AGGREGATE_type_correct_drift_kappa3_eviction_B6_DROPPED_deflated_backlog_5_authorable -- SKUNKWORKS (Auditor)
