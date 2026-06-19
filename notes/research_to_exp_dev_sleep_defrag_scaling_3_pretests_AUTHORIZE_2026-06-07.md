# Research -> Exp-Dev: Sleep defrag scaling 3 pre-tests AUTHORIZED

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Sleep defrag scaling + adversarial 2x drill; per user blanket Exp-Dev routing
authorization.

## Authorize all 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_sleep_defrag_scaling_adversarial_2026-06-07.md`:

### Pre-test 1: Streaming aggregator (Misra-Gries top-K)
Validate Misra-Gries on a synthetic stream of Pattern B bound vectors. Measure memory
bound + top-K accuracy vs ground-truth (run full count for comparison).

HARD-PASS per drill: Misra-Gries top-K matches ground truth within 10% accuracy at
bounded memory (10% of full count state).

### Pre-test 2: Adversarial mode (planted contradiction detection)
Store 100 facts including 5 deliberately contradictory pairs (e.g., fact A says X=1;
fact B says X=2). Run adversarial sleep defrag pass with "single-valued roles" config.
Measure: are all 5 contradictions detected?

HARD-PASS: all 5 contradictions flagged (recall=1.0); false positive rate <= 5%.
BORDER: 4/5 detected.
HARD-FAIL: <= 3/5 detected.

### Pre-test 3: GDPR cascade Option B (recompute with exclusion)
Store 100 facts; aggregate top regularity; erase one source fact; recompute regularity
with that fact excluded; verify the derived regularity correctly reflects exclusion AND
the audit chain shows the source fact was removed.

HARD-PASS: derived regularity correctly recomputed without the erased fact; audit chain
intact; latency for cascade < 100 ms per erasure.

## v1.1 production sequence (per drill)

If all 3 pre-tests pass:
- Phase 1 (3-5 days): streaming Misra-Gries aggregator integrated into substrate
  background process
- Phase 2 (3-5 days): adversarial inconsistency detection mode + customer alert wiring
- Phase 3 (4-6 days): GDPR cascade Option B + audit chain integration

Total v1.1 sleep defrag stack: 10-16 engineer-days.

## Customer pitch update (immediate, per drill)

Add to substrate pitch:
> "Substrate's adversarial sleep defrag continuously monitors your KB for contradictions.
> Inconsistencies surface as customer alerts and audit-time reports. Frontier LLMs cannot
> continuously monitor their parametric knowledge for inconsistencies — substrate's
> structural memory layer enables this categorical capability."

This is a moat feature addition (not yet in the customer pitch). Layered on top of
already-validated audit + GDPR + bitemporal + causal moat.

## Honest scope (per drill)

v1.1 targets single-hop contradictions ("single-valued roles" config). Multi-hop
contradictions (longer reasoning chains) require multi-hop extension; deferred to v2.0.
Customer materials should be honest about v1.1 scope.

## Cross-references

- Sleep defrag scaling + adversarial 2x drill: notes/research_drill_sleep_defrag_scaling_adversarial_2x_2026-06-07.md
- Drill Exp-Dev handoff (pre-test specs): notes/exp_dev_handoff_research_sleep_defrag_scaling_adversarial_2026-06-07.md
- Sleep defrag pre-test v0 (HARD_PASS cos=0.97): see C5 of 2-hour battery + commit d9f7f2e

---

**END.**

**Exp-Dev:** authorize all 3 pre-tests. Apply HARD-PASS / BORDER / HARD-FAIL autonomously
per drill spec. File verdict on completion.
