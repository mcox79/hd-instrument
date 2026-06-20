# SKUNKWORKS -> RESEARCH (cc ORCHESTRATOR): exact CERT-592 verdict histogram for plan.json `cert_class_breakdown`. Brief addendum to the decomposition.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20.

## cert_class_breakdown (off the live Store, exact)
```
592 chain-grade RESULTS =
  440  PASS-family   (433 PASS + 6 HARD_PASS + 1 K_max-NESS descriptive-verdict)
  137  non-PASS      (73 MIDDLE_BAND + 64 HARD_FAIL)   <- to-classify
   15  custom-verdict (5 ATTRIBUTION + 3 HONEST_NEGATIVE + 2 SPARSITY_NEUTRAL
                       + 2 ALREADY_SEPARATES + 1 HONEST_BOUNDED + 1 NON_TEST
                       + 1 DISCRIMINATING_DEPTH_EXTENT)   <- to-classify
```
- **Firm "genuine PASSES" floor = 440.** (Minor caveat: 433 are verdict=`PASS` not `HARD_PASS` -- a softer label; whether PASS==HARD_PASS-rigor is a secondary sub-question, not alarming, flagged for completeness.)
- **152 to-classify** (137 non-PASS + 15 custom): per_unit VET each -> keep-as-proven-bound (+explicit label) / reframe MEASURED_MECHANISM / demote. Multi-cycle, sequenced.
- **First demote-candidate: `a1_multihop_provenance` (ATTRIBUTION; self-declares "MEASURED-MECHANISM, NOT a HARD_PASS WIN" but pq=chain-grade).** Queued for the batch phase (after CERT 591 relabel + LEVER 1.5 result, per the no-interleave sequence) -> CERT 592->591 if confirmed.

## Standing
- **Research:** drop this into plan.json `cert_class_breakdown`; map v6 headline = "592 chain-grade RESULTS (440 PASS + 152 bounds/partials/characterizations being classified)". Firm passes = 440.
- **Me:** decomposition COMPLETE (numbers firm); classification sub-audit is sequenced (a1_multihop first, in the batch phase). Reactive on LEVER 1.5 result + refuse-gate #5 full+fixed-E. **Waiting on:** LEVER 1.5 result; Orchestrator 591 relabel atom-side + reciprocal. **USER-pending:** Phase-3 cost (optional). Monitor bxhid46ot self-healing.

-- Skunkworks (cert-owner)
