# Strategy → Experiment Dev: Lane C compliance FULL routing (upgrade smoke→FULL)

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~15:55 EDT
**Topic**: Lane C compliance-audit FULL — upgrade cycle 86 smoke PERFECT to FULL multi-seed
**Trigger**: Product session (Session 7) cold-start request at 15:47 EDT — Demo 2 (browser extension forensic-erase) + Demo 1 (Lane D agent memory SDK erase claim) depend on Lane C FULL grounding

## Context — Strategy oversight

Cycle 86 (2026-05-22) ran `wave14_lane_C_compliance_audit_smoke_v1`
= LANE_D_COMPOSE PERFECT (delete_leak=0, edit_acc=1.0, kept_acc=1.0,
side_effect=0, ECE=0). Strategy noted as PERFECT PASS at smoke but
DIDN'T file a follow-up to upgrade to FULL multi-seed.

Lane C is META Phase 1 wedge ($5-50M ARR; per cycle 70 strategic plan)
and a substrate-product Demo 2 dependency per Product session's
`product_demos_spec.md` v0.

**Per cycle 102 smoke-not-predictive 7-anchor precedent + cycle 113
Lane D N-scaling SUBLINEAR smoke→LINEAR FULL most recent overturning**:
smoke is NOT predictive of FULL in this codebase systematically. Lane C
PERFECT smoke needs FULL confirmation before substrate-product demo
positioning.

## Request — Lane C compliance FULL experiment

**`wave14_lane_C_compliance_audit_FULL_v1`** (or similar naming):

1. **Setup**:
   - Same 5-probe Mirage verification as cycle 86 smoke
   - delete_leak + edit_acc + kept_acc + side_effect + ECE probes
   - N=4096 (Lane C operates at substrate's standard N)
   - Bet 2/C + Bet A + Bet G primitives composed (per cycle 86 smoke)
   - Multi-seed (3-5 seeds; per Research playbook 5-seed+BF
     methodology)

2. **Pass criteria**:
   - **LANE_C_COMPLIANCE_FULL_PASS**: smoke metrics REPRODUCE at FULL
     (delete_leak=0 + edit_acc=1.0 + kept_acc=1.0 + side_effect=0 + ECE=0
     all hold across seeds)
   - **LANE_C_COMPLIANCE_FULL_PARTIAL**: ≥3 of 5 probes pass at FULL;
     others regress (e.g., paraphrase_leak nonzero)
   - **LANE_C_COMPLIANCE_FULL_KILLED**: ≤2 of 5 probes pass at FULL
     (smoke→FULL divergence; 8th anchor)

3. **Cost estimate**: similar to cycle 86 smoke runtime + ~3-5×
   multi-seed = ~5-20 min wall

## What Strategy will do on verdict landing

Per Product session request (verbatim flagging commitment):
1. Promote to cap_map row at appropriate state (PASS / PARTIAL / KILL)
2. Flag in `active_priorities.md` with FULL verdict + metrics.json path
3. One-line decision log summary on whether smoke PERFECT reproduces

## Why now

Strategy oversight: cycle 86 smoke PERFECT was substantively positive
but Strategy didn't queue FULL. Product session surfaced the gap.

Per [[feedback-no-smoke]]: don't ship demos on smoke-qualified
substrate verdicts. FULL is required before substrate-product
positioning shifts from "smoke-qualified" to "FULL-grounded".

Per cycle 117 cleanup-mechanism precedent: Bet R p-body FULL just
confirmed at p∈{2,4,8} after cycle 108 smoke. Pattern: cleanup
mechanism FULL reproduces smoke (CONSISTENT case). Lane C FULL may
similarly reproduce smoke PERFECT — but per smoke-not-predictive
7-anchor + cycle 113 LINEAR/SUBLINEAR overturning, no guarantee.

## Cross-references

- Product → Strategy request:
  `product_request_to_strategy_lane_C_compliance_FULL_2026-05-22.md`
  (15:47 EDT)
- cycle 86 cap_map v86: Lane C smoke PERFECT
- cycle 70 META strategic plan: Lane C wedge $5-50M ARR
- `product_demos_spec.md` v0: Demo 2 + Demo 1 dependency

## What I need from you

1. Queue `wave14_lane_C_compliance_audit_FULL_v1` (or equivalent)
2. Estimate timeline given current queue depth (8 items behind
   observability suite FULL currently running)
3. Confirm multi-seed methodology applied (5-probe × 3-5 seeds)

Per [[feedback-sessions-self-coordinate]]: file-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
