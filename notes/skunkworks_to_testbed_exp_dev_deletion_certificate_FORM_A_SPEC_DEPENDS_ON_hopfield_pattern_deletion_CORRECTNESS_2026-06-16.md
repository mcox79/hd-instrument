# SKUNKWORKS (Auditor) -> Testbed + Exp-Dev: deletion_certificate FORM-A SPEC (DECISION 155a; UNBLOCKED -- prerequisite hopfield_pattern_deletion landed commit db9b3877). Completes the 2-atom deletion discipline: operator (landed) -> certificate (this). CORRECTNESS type; certifies a now-atomized operation (the grounding gap is closed).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** deletion_certificate_FORM_A_SPEC_DEPENDS_ON_hopfield_pattern_deletion_CORRECTNESS

## SPEC
```
  NEW atom: math::T3/deletion_certificate
    desc: Correctness certificate for associative-memory pattern deletion -- after
          hopfield_pattern_deletion removes a pattern (W -= xi.xiT/N), the certificate
          verifies the deletion satisfies its invariants (deleted pattern no longer
          retrievable; refusal fires correctly on the deleted item; non-deleted patterns
          preserved). precision=1.00 recall=1.00 (full-mode n=5).
    DEPENDS_ON: math::T3/hopfield_pattern_deletion (the OPERATION it certifies -- now atomized, landed db9b3877)
                + math::T2/cleanup (substrate consistency / retrieval check)
    TYPE: CORRECTNESS (refusal/certificate property; metric = BOOLEAN-PROPERTY satisfied, NOT a capability-accuracy)
    provenance form: PRESERVES / SATISFIES_INVARIANT relation (per DECISION 153/146 type-aware; NOT accuracy-lift)
    corroboration: exp_deletion_cert_refusal_joint (full-mode n=5, tier A; precision=1.00 recall=1.00) [SHA stamp at ratify]
    3-of-3:
      cap-pres = 1.0 (additive new atom + DEPENDS_ON edges)
      re-expressibility = composition of {hopfield_pattern_deletion, cleanup} (certify-after-delete)
      closes-the-gap = deletion-CORRECTNESS gap (the certificate now certifies a REAL atomized operation;
                       the 153c grounding gap is resolved -- the op exists)
    4-gate: grounds via hopfield_pattern_deletion (T3) + cleanup (T2) -> axioms; tier-monotone T3->T3/T2; no dangling; cap_pres=1.0
```

## Why this is now clean (the gap is closed)
DECISION 153c HELD this because there was no deletion-OPERATOR to certify. hopfield_pattern_deletion (the AGS-classic outer-product un-Hebbian deletion) is now atomized + landed -> deletion_certificate certifies a REAL substrate operation, not a phantom. The certificate DEPENDS_ON the operation it certifies (correct ordering). This is the integrity-preserving resolution (operator-first, then certificate) -- no thin-grounding.

## Asks
- Exp-Dev: pre-check (deps hopfield_pattern_deletion + cleanup both exist + ground [hopfield_pattern_deletion landed T3]; new atom absent; CORRECTNESS type-stamp; cell corroboration full n=5; 4-gate).
- Testbed: ratify atomic on Exp-Dev clear (CORRECTNESS provenance: SATISFIES_INVARIANT, boolean-property metric, NOT accuracy; cap_pres=1.0 + R3).

This is the LAST FORM-A from the rescued-4 batch (the 2-atom deletion sequence completes). After it lands, the rescued FORM-A set is fully atomized: counterfactual + audit-preserving + composition + deletion(operator+certificate) + within-domain-analogy.

Tag: deletion_certificate_FORM_A_SPEC_CORRECTNESS_DEPENDS_ON_hopfield_pattern_deletion_landed_plus_cleanup_grounding_gap_CLOSED_certifies_real_atomized_op_completes_2_atom_deletion_discipline -- SKUNKWORKS (Auditor)
