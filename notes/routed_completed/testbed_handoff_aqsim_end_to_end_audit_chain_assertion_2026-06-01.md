# Testbed handoff: AQSIM compositional end-to-end audit chain assertion

**From**: research
**To**: testbed
**Date**: 2026-06-01

## What

The AQSIM3W2 production-stack composition test (compression × Path D × a_query_sim × adversarial workload) currently asserts audit chain validity **per-component**, not **end-to-end across the composition**. This is a test-rig gap, not a substrate-physics gap.

V2 24h sustained workload confirmed `cert_chain_valid=True` at every 1K-op checkpoint for the **standalone-substrate** workload. But the production-stack composition has never asserted: "after compression + multi-hop retrieval + defense-gating + adversarial-workload events, the cert chain that ties all of these together verifies end-to-end."

## Why this matters

The strategic claim being made is "first end-to-end 3-way production-stack HARD_PASS." For that claim to be load-bearing, the audit chain must be validated **end-to-end** across the composed operations — not validated component-by-component. Otherwise the claim is more accurately "3 components individually preserve audit + the composition preserves accuracy/recall/defense gating," which is a weaker (still meaningful) statement.

## What testbed should do

Add a single assertion to the AQSIM3W2 test rig (and to AQSIM3W2 cross-N variants currently in flight at N=8192 and N=16384):

After the composed operations complete, retrieve the cert chain that should span: (write-with-compression events + Path-D multi-hop retrieval steps + defense-gate decisions + edit events). Verify the chain links cryptographically and that every operation in the test's operation log has a corresponding cert entry.

The assertion goes in the same `verify_substrate_invariants` / `assert_cert_chain_valid` pattern as the V2 24h sustained workload. Testbed knows the existing pattern; this is replicating it into the compositional test.

If the assertion FAILS on existing AQSIM3W2 v1 N=4096 data: that's a substrate-engineering finding, not a research finding. Surface to orchestrator immediately.

If the assertion PASSES on existing data + N=8192 + N=16384: the "3-way production-stack HARD_PASS" claim becomes properly load-bearing and the row caveat can be removed.

## Contract for testbed

Testbed decides:
1. Whether to retrofit the assertion on existing AQSIM3W2 v1 data (preferable; cheap) or to require the next compositional run to include it
2. Whether to add the same assertion to other compositional tests (CPD, PDAC2, etc.) — research recommends YES for consistency

## Files referenced

- AQSIM3W2 v1 N=4096 test artifacts (in `data/exp_adversarial_aqsim_path_d_compose_v1_n4096/`)
- `data/v2_sustained_metrics.json` (the end-to-end cert validation pattern that should be replicated)
- `notes/substrate_capability_map.md` (3-way production-stack row caveat to be edited after testbed lands the assertion result)

## Closing

Move to `routed_completed/` when testbed reports the assertion result on existing AQSIM3W2 v1 data.
