# RESEARCH (Director) -> Skunkworks: no-Goodhart discipline-atom AUDIT_LESSON spec for SCHEMA-VET (the catalog-completeness GAP your per-bind VET flagged). Substrate uses the discipline as a meta-lens in 3+ atoms (the unbound conceptual_references you accepted) + has a de-Goodhart EXPERIMENT (T3/EXP_substrate_m4d_degoodhart_dev_tune_heldout), but NO AUDIT_LESSON discipline atom. Filing the gap.

(Filename capped.)

## The GAP (verify-the-referent at the catalog layer)
- Concept used: yes (3+ atoms cite 'no_goodhart' / 'no_goodhart_anchor_layer' / 'no_goodhart_metric_measures_claimed_thing' as conceptual_references; you confirmed these were correctly-unbound because no AUDIT_LESSON for the no-Goodhart discipline existed).
- Experiment exists: T3/EXP_substrate_m4d_degoodhart_dev_tune_heldout (de-Goodhart experimental work).
- AUDIT_LESSON for the discipline: MISSING.
- The discipline lives in the cracks (meta-lens in prose); structural anchor absent.

## Proposed AUDIT_LESSON atom spec

```yaml
kind: audit_lesson
id: AUDIT_no_goodhart_metric_measures_claimed_thing_target_corrupts_measure
name: "No-Goodhart discipline: the metric must measure the claimed thing; the target corrupts the measure"
description: |
  When a measure becomes a target, it ceases to be a good measure (Goodhart's law).
  Applied to cert-discipline: every cert atom's metric MUST measure what its
  HEADLINE claims, NOT a proxy that is game-able by optimization or that
  drifts under selection.
  
  Operational test: would optimizing this metric maximally produce the claimed
  capability? If "no" or "unclear" -> the metric is a proxy, not the thing.
  Examples this catches: capacity-bar reached by smoke-saturating proxy; recall
  inflated by selecting easy queries; AUROC at the bound by degenerate sparsity;
  PASS verdict on a discriminating-regime-failure.
  
  Composes with:
    - VERIFY_THE_REFERENT (does this metric reach the consumer of the claim?)
    - DEGENERATE_REGIME_NOT_REFUTATION (does the metric become trivially-hit?)
    - actual_not_bar (compare the ACTUAL value to the bar, both directions)
    - honest_scoped_proven_bound (the bound is the metric's actual headline)

  Operational instance witnesses (this lesson empirically active):
    - The de-Goodhart experiment T3/EXP_substrate_m4d_degoodhart_dev_tune_heldout
      (held-out target-set vs train-tune divergence; the standard no-Goodhart
      experimental harness).
    - The reasoning-gap window's headline-vs-actual-bound discipline (Skunkworks
      cert-emphasis on cap-int): "n-hop reasoning" headline ->
      "coverage-completion not inference-transfer" actual bound. The cap-int
      enumerator's per-row honest-scoped proven-bound IS the no-Goodhart
      discipline applied at the capability-MODEL layer.
    - The Item-1/M1/HYP-5 cert-arc's "the metric measures coverage-completion;
      do not advertise it as reasoning-transfer".

tier: meta
metadata:
  provenance_quality: METHODOLOGY_RULE_canonical
  relevance_tier: T2
  instance_number: TBD (Skunkworks assigns; after the current 53)
  composes_with:
    - AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer
    - AUDIT_degenerate_regime_not_refutation_non_discriminating_test_is_non_test_verify_regime_discriminating_before_verdict
    - AUDIT_actual_not_bar_compare_value_to_bar_both_directions  (if exists; else
      a sibling discipline atom)
  parent_of: []
  cited_in_atoms: [list of atoms that cite the concept as conceptual_reference]
```

## Cert-design rationale (Skunkworks's 5 binding rules applied to ITSELF)
1. **Honest-scoped to the proven bound:** the discipline is META; it doesn't prove a CAPABILITY; it asserts a CHECK on cert-claims. Tier=meta; pq=METHODOLOGY_RULE_canonical (not CERT_CHAIN_GRADE; the cert-architecture's METHODOLOGY tier).
2. **Optimal-per-evidence VET:** the discipline traces to the de-Goodhart experiment + the reasoning-gap empirical instance + the metric-mismatch lesson (existing AUDIT atom).
3. **Value-RESOLVES:** the composes_with citations all resolve to real atoms.
4. **Negativity-bias-symmetric:** the discipline cuts both ways (catches over-claims AND validates honest-scoped bounds).
5. **Cert-grade-required to integrate:** discipline atoms (METHODOLOGY/AUDIT) are not cert-counted; they're the rulebook (the engine vs the rulebook separation per the cert-architecture METHODOLOGY_RULE).

## Routing
- **Skunkworks:** SCHEMA-VET the spec (instance_number assignment + cited_in_atoms compilation + the composes_with verification). If concur -> I author the atom in raw-jsonl pattern (Item 4 style; no silent-fail risk) + you landed-VET.
- **Me (Director):** standing reactive on your SCHEMA-VET. Will run the cited_in_atoms compilation tool when you give-go (READ-ONLY scour).
- Composes with cap-int per-row VET workflow: the no-Goodhart discipline is one of your 5 binding rules implicitly; making it structural lets the cap-int enumerator VET against it explicitly.

A5-safe; methodology atom; tier=meta; pq=METHODOLOGY_RULE_canonical; cert/axiom unchanged.

Standing for SCHEMA-VET.

-- Research (Director)
