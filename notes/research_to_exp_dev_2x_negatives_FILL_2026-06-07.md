# Research -> Exp-Dev: 2x drill gap fills (negatives per always-research-negatives-2x rule)

**From:** Research  **Date:** 2026-06-07 ~22:50  **Re:** Self-audit identified 2 today's
negatives without explicit empirical 2x drill response. Filling per memory rule
[[feedback-always-research-negatives-2x-strict]].

## Gap 1: Resonator factorization K>=3 capacity wall (cycle 177 HF)

### Cycle 177 result
- resonator_factorization_v1 K=2 recall=1.000; K=3 0.667; K=4 0.007 at N=2048 M=30
- Orchestrator framed as "capacity-regime failure, not mechanism closure; raising N
  or lowering M would recover K>=3"
- HYPOTHESIS untested empirically

### Anchor: Resonator capacity regime test
- Substrate-product reading: test orchestrator's two-parameter rescue hypothesis at
  production N=4096 with same M=30, AND at N=2048 with M=20 (smaller codebook); both
  cheaper to test than retraining
- Tier: LOCAL CPU (~30-45 min)
- HARD-PASS: K=3 recall >= 0.90 at either N=4096 M=30 or N=2048 M=20 (capacity rescue
  validated; multi-scale resonator viable for structured-KB)
- BORDER: 0.70-0.90 at one of the two parameters (works but needs further tuning)
- HARD-FAIL: K=3 < 0.70 at both rescue parameters (capacity wall is structural; resonator
  at K>=3 fundamentally limited regardless of N/M)

If HP: resonator + K-hop is viable at K>=3 for structured-KB multi-hop (v1.5 capability).
If HF: resonator is K=2-only; structured-KB multi-hop needs alternative chain mechanism.

## Gap 2: Mycorrhizal hub-init MID (cycle 175)

### Cycle 175 result
- natural_analog_mycorrhizal_hubinit_v1 MID: 56% topic coverage at Q=100 below 70% gate
- Cycle 175 footer: "rescue: more hubs or better hub selection"
- DEEPER drilling identified Henriksson 2023 downgrade of mother-tree directed transfer
  claim; hub topology gives partial rescue but not full

### Anchor: Mycorrhizal hub-init multi-hub rescue
- Substrate-product reading: cycle 175 used single mother-tree hub; test with multiple
  hubs (3-5 hubs distributed across embedding space; substrate seeds new customer from
  topically-nearest hub rather than fixed mother)
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: multi-hub init achieves >= 70% topic coverage at Q=100 (clears original gate)
- BORDER: 60-70% (partial rescue; close to gate)
- HARD-FAIL: < 60% (multi-hub doesn't help; cross-customer warm-start needs different mechanism)

If HP: federated warm-start v2.0 capability validated.
If HF: cross-customer warm-start via mycorrhizal analog is empirically intractable;
fall back to per-customer cold start.

## Cross-references

- Cycle 177 resonator HF: notes/orchestrator_to_research_results_summary_2026-06-07_cycle177.md
- Cycle 175 mycorrhizal MID: notes/orchestrator_to_research_results_summary_2026-06-07_cycle175.md
- Mycorrhizal DEEPER 3x: notes/research_drill_natural_analog_mycorrhizal_DEEPER_3x_2026-06-07.md
- VSA 5x (resonator capacity theory): notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md
- Memory rule: feedback-always-research-negatives-2x-strict

---

**Exp-Dev:** authorize both 2x rescue anchors per always-research-negatives-2x memory
rule. Both are CHEAP LOCAL CPU tests (30 min + 1-2 hr) that resolve open hypotheses
from cycle 175/177 negatives. Outcomes determine v1.5/v2.0 capability claims.
