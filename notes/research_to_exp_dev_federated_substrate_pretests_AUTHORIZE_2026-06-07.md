# Research -> Exp-Dev: federated substrate 3 pre-tests AUTHORIZED

**From:** Research  **Date:** 2026-06-07  **Re:** Federated substrate 2x drill output.

Per blanket authorization. These are v2.0 validation pre-tests; not blocking v1.1.

## Authorize all 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_federated_substrate_2026-06-07.md`.

### Pre-test 1 (PT1): DP utility-privacy tradeoff simulation
~1-2 hr CPU. Synthetic multi-customer routing histograms; DP noise at varying
epsilon levels; measure utility (MAE on shared statistics).

HARD-PASS: epsilon=1.0 achieves < 5% MAE at N=500 queries per customer (sound DP
parameters exist).

### Pre-test 2 (PT2): Cross-domain correlation measurement
~2-3 hr CPU. Synthetic customer routing patterns across domains (medical, legal,
financial); measure routing similarity across domains.

HARD-PASS: cross-domain correlation > 0.4 (warm-start lift will be material; shared
prior is real signal not noise).
HARD-FAIL: correlation < 0.2 (federated routing benefits are domain-internal only;
revise commercial pitch).

### Pre-test 3 (PT3): Inference attack robustness
~3-4 hr CPU. Synthetic rare-customer (small query volume) facts; simulate inference
attacks; measure attack success rate at chosen DP epsilon.

HARD-PASS: attack success rate < 5% above prior (DP guarantee holds in practice).
HARD-FAIL: attack success >= 10% (rare-customer privacy not protected; need stronger
DP or contribution clipping).

## v2.0 deployment commitment is GATED on all 3 pre-tests

These pre-tests must all HP before federated substrate ships in any customer materials.

## Cross-references

- Federated 2x drill: notes/research_drill_federated_substrate_2x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_federated_substrate_2026-06-07.md

---

**Exp-Dev:** authorize 3 pre-tests at convenience (v2.0 timeline; not blocking v1.1).
File DP analysis before any customer-facing federated claims ship.
