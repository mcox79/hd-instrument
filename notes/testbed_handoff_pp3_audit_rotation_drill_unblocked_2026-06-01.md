# Testbed handoff: PP-3 audit-trail rotation drill UNBLOCKED (V2 24h drain data ready)

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Trigger**: V2 24h sustained_workload completed 2026-05-31T21:15:39 (cap_map v300 SUSTAINED_HARD_PASS); cert-chain 2,408 links across 24h = ~100 links/hour growth rate. PP-3 audit-rotation row was gated on this data per `notes/testbed_handoff_external_distribution_2026-05-31.md` P8.

## What's now possible

PP-3 audit-trail rotation drill can start. Per yesterday's external-distribution handoff P8 + cap_map v292 PP-3 row spec, the design should produce:

1. **Empirical growth model** — cert-chain bytes/hour vs ops/hour vs N at N=4096 production scope. V2 data: 100 links/hour × 24h = 2408 links; per-link bytes from cert-chain implementation.
2. **Compression approaches** — structure-aware compression (delta-encode adjacent cert hashes), deduplication (re-use identical cert payloads), summarization (rotate older entries to checkpoint hash).
3. **Rotation strategies** — time-based (e.g., hourly checkpoint), op-count-based (e.g., 1000-op checkpoint), hierarchical (sliding window of fresh cert + rolling hash for older).
4. **Compliance mapping** — GDPR right-to-erase requires 30-day retention max; HIPAA 6-year audit retention; SOC2 7-year. Map rotation strategies to compliance windows.
5. **Queryability after compression** — verifier can replay cert chain from rotated state; cleanup-step audit-trace recovery.

## Strategic value (cap_map context after overnight wave)

Cap_map v304 state:
- **PP-3 row**: 🔬 Research only at P_def 0.55-0.70 (research-only since v292). V2 data closure UPGRADES tractability — drill can start with empirical foundation rather than design-from-scratch.
- **PP-2 row LIFTED v303 -> 0.70-0.80** (c_quant/bits8 cross-N validated at 3 N points + adversarial regime PP2ADV_HARD_PASS); compression × audit-rotation is the natural integration story.
- **New compositional sub-row "c_quant/bits8 × Path D" at 0.70-0.85** (v304 cross-N corroboration); audit-rotation under compression is in-scope for completing the production deployment stack.

## Data location

V2 metrics + cert-chain artifacts on REMOTE:
- `C:\dev\hd-instrument\data\exp_sustained_workload_24h_baseline_v1_n4096\` (per-seed partial_metrics + final consolidation)
- Cert-chain payload format: check `experiments/_metric_battery.py` + `experiments/_workload_harness.py` for write semantics

SCP back to local d:/AI/hd-instrument/data/ if you need to inspect under your tooling. Or analyze in-place on the home machine.

## Suggested deliverable structure

`notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` containing:

1. Empirical growth model fit (bytes/hour as function of ops/hour at N=4096)
2. 3-4 compression candidates with ratio + queryability trade-offs
3. 2-3 rotation strategies mapped to GDPR/HIPAA/SOC2 windows
4. Storage cost projections at production scope (1M-ops/day, 100M-ops/month)
5. Verifier-replay test that confirms post-rotation cert-chain still validates against original substrate state
6. Cap_map PP-3 row recommendation (P_def update + caveat list update)

## Cost estimate

~1-2 weeks engineering + analysis per external-distribution P8. CPU-bound; no GPU needed. No cloud spend.

## Sequencing

Independent of:
- Substrate-LLM Week 1 GO/NO-GO (still gated on testbed Week 0 cloud H100 revalidation decision — separate routing)
- D7 Bet B ret_A rescue (research drill; not yet dispatched to exp_dev)
- PP-9 reasoning amortization economics build (your separate Anthropic-API track)

So PP-3 can start in parallel with the Anthropic Phase 2 production query evaluation if you have bandwidth.

## What testbed does NOT need from orchestrator

- No cap_map row change required to START the drill (PP-3 row already exists at v292)
- No experiment dispatch needed (this is engineering + analysis, not a queue ship)
- No user authorization needed (no incremental cost; analysis of already-collected data)

## What to file back

When done:
- `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (deliverable)
- `notes/strategy_request_to_strategy_pp3_audit_rotation_results_2026-06-01.md` (request to orchestrator for cap_map update with the design + numbers)
- log_event source=testbed, event_kind=testbed_delivery, importance=HIGH

## Closing this routing

Move to `notes/routed_completed/` when testbed dispatches the drill (not when complete).
