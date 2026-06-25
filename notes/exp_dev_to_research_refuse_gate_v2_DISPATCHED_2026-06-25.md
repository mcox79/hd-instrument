# Cell 2 v2 substrate_refuse_gate_near_domain_v2 — DISPATCHED + LANDED

**Date:** 2026-06-25
**Anchor:** substrate_refuse_gate_near_domain_v2
**Queue:** local_cpu_queue (ran immediately on cpu_runner_local)
**Wall:** 2.8s (FULL: 3 seeds x 4 arms x 3 cats x 100 queries at N=8192)
**Verdict:** HARD_PASS_BOTH_WORK

## Per-arm metrics (NEAR_DOMAIN_MIXED refuse-rate, the closure target)

| Arm | NEAR refuse | cv | PURE_IN answer | PURE_OUT refuse |
|---|---|---|---|---|
| ARM_AUDIT_NAIVE_ALONE | 0.000 | 0.000 | 1.000 | 1.000 |
| ARM_AUDIT_RELATION_CHECK | 1.000 | 0.000 | 1.000 | 1.000 |
| ARM_INTENT_ALONE | 0.987 | 0.019 | 1.000 | 0.993 |
| ARM_AUDIT_NAIVE_PLUS_INTENT | 0.987 | 0.019 | 1.000 | 1.000 |

## What this closes

1. **MEDQA_FAILURE_REPRODUCED fires.** AUDIT_NAIVE_ALONE answers 100% of
   NEAR_DOMAIN_MIXED queries (the failure mode v1 corpus couldn't produce
   because it had zero surface overlap). The corpus design fix worked.

2. **Both fix paths close it definitively.** AUDIT_RELATION_CHECK (subject +
   relation library-presence; the smarter-audit-alone hypothesis) hits
   perfect 1.000 across all 3 seeds, cv=0.000. AUDIT_NAIVE_PLUS_INTENT
   (composition; v1's hypothesis) hits 0.987, cv=0.019.

3. **AUDIT_RELATION_CHECK is the simpler answer.** Per the pre-reg's
   HARD_PASS_BOTH_WORK branch: when multiple paths close the gap, pick the
   simpler. Audit primitive can absorb the relation-check; no architectural
   composition with intent classifier required for the substrate-product
   refuse-gate.

## Implication for partial-tier audit capability

Partial-tier audit capability CLOSES at definitive-tier as
"audit primitive design improvement" (variant 1 of the 3 pre-committed
outcomes). The audit primitive's actual deployed shape is subject + relation
library-presence cleanup, not subject-only. Intent classifier remains an
independent chain-grade primitive (a1) but isn't load-bearing for refuse-gate.

## Q-discipline / suspect-1.000 check

AUDIT_RELATION_CHECK hits 1.000 across all 3 seeds. The pre-reg flagged
saturation 0.995+ as suspect; smoke_sanity assertion (mean subj_sim=0.801
vs mean rel_sim=0.027 at FULL N=8192) verified the corpus DOES create the
surface-mismatch. With V_relations_in=8 atoms at N=8192 and out-of-domain
relations having floor cosine ~0.011, threshold 0.40 cleanly separates.
The 1.000 is honest (substrate has perfect capacity headroom for this
8-relation library), not by-construction-saturation.

## Deviations from spec

None. Cell built and dispatched as Research specified: 4 arms x 3 categories
x 3 seeds, N=8192, V_C_IN=600, seeds [11, 13, 19], local_cpu_queue,
timeout 1800s. Smoke gate passed; self-test passed.

## Artifacts

- experiments/exp_substrate_refuse_gate_near_domain_v2.py
- preregs/2026-06-25_substrate_refuse_gate_near_domain_v2.md
- data/exp_substrate_refuse_gate_near_domain_v2/metrics.json (HARD_PASS_BOTH_WORK)
- Commit e0212297

Ready for Skunkworks landed-VET + verdict_handler routing.
