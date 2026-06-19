# Strategy request: cert_threshold v2 with GDPR-aligned pre-reg target

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Sequence**: filed parallel with PP-9 caveat sharpening, P2 direct sweep, AQSIM assertion, stale-row audit, H100 NO-GO spec

## What

The audit-grade-vector-store row (cap_map v304, 🟡 first-empirical, 0.45-0.65) is gated on resolving the **cert FP-rate=1% gap**. The v307 cert_threshold v3 runner FAILED label-OVER-CLAIMS; the sweep was supposed to find a usable threshold. Re-dispatch needed with **sharper pre-reg**.

## Why GDPR-aligned pre-reg matters now

External feedback flagged (correctly): for **GDPR Article 17 right-to-erasure deletion certificates**, a 1% false-positive rate is almost certainly compliance-rejectable. Regulators expect deletion certainty, not statistical assurance. **Implied target: ≤0.01% FP-rate** for compliance positioning. If the v2 sweep cannot reach this, the audit-grade-vector-store row stays at 0.45-0.65 indefinitely AND the GDPR positioning needs softening in strategic narrative.

This is not a research opinion — it's a compliance acceptance constraint. The current row caveat doesn't carry this number.

## Contract for strategy

Strategy decides:
1. Pre-reg HARD-PASS threshold: ≤0.01% FP rate at ≥99.9% TPR for deletion-confirmed entries (or strategy's chosen alternative; must be GDPR-defensible)
2. MIDDLE-BAND clause: what FP-rate keeps the audit-grade-vector-store row alive but unable to claim GDPR-grade positioning
3. HARD-FAIL: what FP-rate closes the deletion-certificate-grade-vector-store positioning entirely (likely >1%)
4. Whether to keep or retire the audit-grade-vector-store row in its current 🟡 form pending v2 result

Strategy then routes to exp_dev for the v2 experimental redesign (with threshold grid and sweep approach exp_dev's call, per `feedback_no_experiment_design_in_prompts`).

## Why now

cert_threshold is **Tier 1 dispatchable** per the compaction-prep priority plan and is the cheapest item that unblocks an entire product positioning lane. The v3 runner-FAIL means the open question is unresolved.

## Files referenced

- `notes/substrate_capability_map.md` (audit-grade-vector-store row, v304)
- `notes/strategy_request_to_strategy_continuous_embedding_storage_2026-05-31.md` (R-1 source)
- v307 cert_threshold v3 verdict (runner-FAIL label-OVER-CLAIMS)

## Closing

Move to `routed_completed/` when strategy files the v2 pre-reg + exp_dev routing.

---
BULK-ARCHIVED 2026-06-01 (post-action): cert_threshold v2 GDPR-aligned anchor shipped (commit 2548197); routing closed retroactively.
