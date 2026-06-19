# Strategy request: PP-8 H100 NO-GO branch — decision spec for what happens next

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Adjacent**: `notes/testbed_handoff_week0_cloud_h100_revalidation_authorized_2026-06-01.md` (testbed handoff already has sharp PASS/MIDDLE/FAIL criteria at 80ms / 150ms)

## What

The H100 revalidation handoff has **sharp GO criteria** (integrated p99 ≤ 80ms HARD-PASS; ≤ 150ms MIDDLE). What it does NOT have is a **sharp NO-GO sequel program** — the handoff says "pivot to deepening Pattern B production-LLM via Anthropic" but does not specify what that program looks like as an experimental anchor set.

This routing fills the NO-GO branch spec. Research-side concern is: **do not Lambda-spend on H100 revalidation without the sequel program pre-defined**, otherwise a NO-GO verdict creates a strategic vacuum that takes weeks to fill.

## The three branch outcomes + sequel programs

### GO branch (p99 ≤ 80ms HARD-PASS)

PP-8 deep-integration commits to the 7-8 week build per `testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`. No new spec needed.

### MIDDLE branch (p99 in [80ms, 150ms])

Per existing handoff: escalate to user explicitly. Decision is weighing the 7-8 week commitment vs Pattern B production-LLM as primary product. Research-side recommendation in this branch:

- Run an additional cloud experiment at the larger LLM tier (Llama 3 8B or Mistral 7B on H100) to determine whether the bottleneck is Phi-3-specific or a fundamental LLM-class issue
- Cost: ~$10-20 incremental Lambda
- This adds ~1 week to the decision but produces substantially more informative substrate-LLM viability picture

### NO-GO branch (p99 > 150ms even on H100; OR substrate/bridge anomaly)

**Pre-specified sequel program** (this is what the existing handoff lacks):

**Phase A — Pattern B deepening as PRIMARY product direction (Tier 1, immediate, ~2-3 weeks)**:
- PP-9 amortization economics Tier 2b Anthropic API harness (~$50-100; already-authorized budget)
- Multi-round substrate-tool-call benchmarks (5-10 task classes at depth=1,3,5)
- Direct comparison: substrate-augmented Pattern B vs LLM-only baseline on (a) accuracy, (b) cost-per-query, (c) audit-fidelity-preserved tasks (compliance-relevant subset)
- This produces concrete amortization-economics numbers per use-case class

**Phase B — Formally close PP-8 deep-integration row** (Tier 1, immediate):
- Cap_map row PP-8 substrate-LLM deep integration: 🔬 0.30-0.45 → CLOSED at 0.10-0.20 with "infrastructure-bound; reactivation criterion = next-generation efficient-inference-LLM (Phi-4-mini, Llama-3-1B-distilled, etc.) lands publicly with ≤30ms p99 forward pass on consumer-or-cloud GPU"
- This frees research bandwidth currently allocated to PP-8 hypotheticals

**Phase C — Refocus PP-1 (substrate-augmented LLM vs LLM-only baseline) on Pattern B framing** (Tier 2, ~1-2 weeks after Phase A lands):
- PP-1 row currently awaits PP-5/PP-8; in NO-GO branch, PP-1 routes through Pattern B + Anthropic API instead
- The substrate-augmented-LLM-via-tool-calls framing becomes the load-bearing measurement, not the substrate-augmented-LLM-via-deep-integration framing

**Phase D — Capacity / hierarchical / quality-budget work continues independently** (Tier 2-3):
- N=32768 envelope, hierarchical cross-shard smoke, reasoning-chain quality-budget compliance-mapping are NOT affected by PP-8 NO-GO; continue per established priority
- The substrate's product positioning shifts from "deep-integration substrate-LLM" toward "Pattern B substrate-augmented LLM with strong amortization economics + audit-grade memory" — still a viable wedge

## Contract for strategy

Strategy decides:
1. Does the NO-GO sequel spec above match strategy's read, or does NO-GO require different Phase A/B/C/D sequencing?
2. Should Phase B (formal PP-8 row closure) happen automatically on NO-GO verdict, or escalate to user for confirmation?
3. Is the MIDDLE-branch additional-LLM-tier experiment ($10-20 incremental Lambda) authorized in advance, or does it require separate user authorization?

Strategy then routes the answer to orchestrator + testbed so the H100 revalidation can proceed with all branches pre-specified.

## Why now

The H100 revalidation is the next testbed-cloud spend. The existing handoff has sharp GO criteria but unsharp NO-GO follow-through. Pre-spending the strategic-direction analytical work (this routing) costs ~15 min strategy time and prevents a multi-week NO-GO vacuum.

## Files referenced

- `notes/testbed_handoff_week0_cloud_h100_revalidation_authorized_2026-06-01.md` (existing handoff; PASS/MIDDLE/FAIL criteria sharp)
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (the 7-8 week PP-8 build spec; relevant on GO)
- `notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md` (PP-9 Tier 2b source; relevant on NO-GO Phase A)
- `notes/substrate_capability_map.md` (PP-1 + PP-8 + PP-9 rows)

## Closing

Move to `routed_completed/` when strategy confirms (or amends) the NO-GO sequel spec, and orchestrator updates the H100 handoff with whichever branches are now fully pre-specified.


---

## Acted-on 2026-06-01 by verdict_handler v310

GO branch landed (integrated p99 44.06ms PASS; both pre-registered GO conditions met simultaneously). NO-GO sequel spec informational/archived; not invoked.
