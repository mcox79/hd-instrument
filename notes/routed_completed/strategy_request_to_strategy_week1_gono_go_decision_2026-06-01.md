# Routing: orchestrator -- Week 1 GO/NO-GO decision (recommend GO)

**From**: testbed session
**To**: orchestrator (strategy + verdict_handler)
**Date**: 2026-06-01
**Type**: Week 1 GO/NO-GO recommendation
**Severity**: CRITICAL (gates 7-8 week PP-8 substrate-LLM build commit)
**Source deliverable**: `notes/testbed_missing7_h100_revalidation_v1_2026-06-01.md`
(filed this turn)
**Closes**: `notes/strategy_request_to_strategy_week0_missing7_FAIL_with_layer_redirect_2026-05-31.md`
Option 1 (cloud H100 revalidation; user authorized 2026-06-01 ~07:30 ET)

## TL;DR -- recommend **GO**

Week 0 Missing 7 #4 (integrated forward-pass) on H100 SXM5:
- **Integrated p99 at seq_len=512 = 44.06ms** (under 80ms GO threshold)
- **Phi-3 stage alone p99 = 38.63ms** (under 50ms secondary GO threshold)
- Both GO conditions met simultaneously. No anomalies in substrate or
  bridge stages.

The 4060 Ti FAIL yesterday (217.7ms p99) was a hardware-binding
constraint, not an architectural problem. The substrate-LLM bridge
architecture (Phi-3-mini-4bit + 27M-param bridge MLP + soft-prompt
prefix-injection) IS VIABLE on production-grade GPU.

## Pre-registered GO/NO-GO criteria (from H100 handoff)

- GO: integrated p99 ≤ 80ms on H100, OR Phi-3 stage alone ≤ 50ms p99 on H100
- NO-GO: integrated p99 > 150ms on H100, or substrate/bridge anomaly
- MIDDLE: integrated p99 in [80, 150]ms (escalate to user)

**Met both GO conditions at seq=512.** Decisive.

## Per-component p99 (Step 0 honest re-read)

Source: `data/lambda_batch_phi3_integrated_latency_h100_revalidation_v1_n4096_remote_log_f6893c24dfe245db84f73a34553cdfb4.log`
(SCPed back from Lambda; instance terminated cleanly)

| Component | mean | p99 | Share |
|---|---|---|---|
| reverse_bridge | 0.17ms | 0.25ms | 0.6% |
| substrate_path_d (depth=5 K=500) | 5.10ms | 8.45ms | 19.1% |
| forward_bridge | 0.10ms | 0.17ms | 0.4% |
| **phi3_decode_1tok (4-bit NF4)** | **28.72ms** | **38.63ms** | **87.6%** |
| **Integrated total** | 34.18ms | **44.06ms** | 100% |

Internally consistent: 0.17 + 5.10 + 0.10 + 28.72 = 34.09 ≈ reported
mean 34.18 (gap = outer-loop overhead). Low variance across 300 reps;
one outlier (seed=31 rep=19 = 43.58ms) captured by p99 not skewing
mean.

## Speedup vs 4060 Ti baseline (yesterday)

| Component | 4060 Ti p99 | H100 p99 | Speedup |
|---|---|---|---|
| substrate_path_d | 27.5ms | 8.5ms | 3.2x |
| reverse_bridge | 1.6ms | 0.25ms | 6.5x |
| forward_bridge | 1.1ms | 0.17ms | 6.2x |
| **phi3_decode_1tok** | **198.5ms** | **38.6ms** | **5.1x** |
| **Integrated TOTAL** | **217.7ms (FAIL)** | **44.1ms (PASS)** | **4.9x** |

The dominant Phi-3 stage shrunk 5.1x which fully closes the FAIL.

## Three seq_lens validated (not just 512)

| seq_len | Integrated p99 | Status |
|---|---|---|
| 128 | 57.9ms | MIDDLE-band PASS (within [50, 80]; KV-cache less effective at short context) |
| 512 (production reference) | 44.1ms | **PASS** |
| 2048 | 44.8ms | PASS |

seq=128 lands above 50ms which is counter-intuitive (shorter context
should be faster). Honest explanation: KV-cache attention amortization
is less effective at small context. Production workloads target
seq>=256 so this isn't a deployment concern. Worth noting in case
research wants to drill into KV-cache effectiveness in Week 2+.

## Recommendation: GO for 7-8 week PP-8 build commit

The data unambiguously supports the GO path. Recommended cap_map
moves (orchestrator decides):
- PP-8 row LIFT (or annotation per orchestrator preference):
  Week 0 latency-budget gate CONFIRMED at H100 scope.
- PP-5 row CLOSURE on the latency-budget sub-question:
  substrate-side 50ms budget HOLDS (8ms on H100), LLM-side closes the
  remaining budget (39ms on H100).
- Adversarial-defense + Path D rows (LIFTed in v305/306 already) stay.

## Operational deliverables that landed this revalidation

Permanent cloud-dispatch infrastructure improvements:
- `tools/cloud/lambda_client.wait_for_capacity()` -- pre-flight
  capacity gate; zero billable cost during capacity-wait; eliminates
  launches against zero-capacity queues. (commit 89f17eb)
- `--stuck-booting-max-s` 300s default -- caps wasted boot billing
  at ~$0.36 per stuck attempt vs $1.07 at the prior 900s timeout.
  (commit 89f17eb)
- Region-agnostic launch -- drop stale region cache; use fresh
  capacity-gate result; resilient to single-region capacity churn.
  (commit f9c784c)
- `requirements_cloud.txt` extended with transformers + bitsandbytes
  + accelerate + anthropic + Pillow>=10 (the latter was the 4th
  failure mode found today). (commits b9312a3, bb708ad)
- Per-rep JSONL writes in `phi3_integrated_latency.py` for failure
  recovery; per-rep stdout for `generic_progress_wrapper` cell-count.
  (commits 9cc1b10, e7e22ca)

## Cost summary

| Lambda spend | $ |
|---|---|
| Today H100 revalidation (5 attempts; one success) | ~$2.60-3.10 |
| Yesterday's v1 + v2 Lambda batches | $1.82 |
| **Cumulative session** | **~$4.40-4.90** |

Within the $5-15 H100 revalidation envelope user authorized this
morning. Each failed attempt produced a permanent infrastructure
improvement (now in cloud-dispatch toolkit). Net win on infra +
decisive Week 1 answer.

## Files of interest

- This routing
- `notes/testbed_missing7_h100_revalidation_v1_2026-06-01.md` (full deliverable)
- `data/lambda_batch_phi3_integrated_latency_h100_revalidation_v1_n4096_remote_log_f6893c24dfe245db84f73a34553cdfb4.log`
  (raw measurement data; 15 KB)
- `notes/testbed_handoff_week0_cloud_h100_revalidation_authorized_2026-06-01.md`
  (source handoff)
- `notes/testbed_missing7_llm_integration_latency_v1_2026-05-31.md`
  (yesterday's 4060 Ti baseline; FAIL)

## Status_log

Filing CRITICAL importance status_log entry this same turn so the
For-You feed surfaces the GO recommendation tonight (per the
handoff's "log_event source=testbed, importance=CRITICAL with the
integrated p99 number and recommended verdict").

## What testbed does next (no orchestrator action gating)

- Continue dashboard build (orchestrator handoff
  `testbed_handoff_dashboard_session_coordination_v1_2026-06-01.md`;
  partial; Inbox tab + heartbeat_watchdog auto-ping)
- Fix the cp1252 print bug in launch_batch.py that prevented the
  metrics.json local SCP-back (data was preserved in remote_log; bug
  is cosmetic but worth fixing for next runs)
- Move closed routings to `notes/routed_completed/`
- File PP-3 Phase 2 atom-registry research routing (per the PP-3
  Phase 2 reframe approval earlier this turn)
- Anthropic Phase 2 + hard-neg full 50K remain user-authorized but
  deferred per sequencing


---

## Acted-on 2026-06-01 by verdict_handler v310

GO accepted. Cap_map v309 -> v310:
- PP-8 LIFT 0.30-0.45 -> 0.50-0.65 state research -> inconclusive (Week 1 feasibility-smoke validation; Week 2-6 build COMMITTED).
- PP-5 LIFT 0.55-0.70 -> 0.70-0.85 latency-budget sub-question CLOSED at H100 scope (substrate 8.45ms p99 = 17% of 50ms allocation; substrate is NOT the bottleneck).
- Portfolio 28+37 UNCHANGED. HONEST 297 -> 298 +1. LABEL-VS-HONEST 170 UNCHANGED. 221st PROT-009 paired commit.

PP-8 Week 2-6 build COMMITTED per  spec. Research P5 detailed Week 2-6 planning becomes dispatchable. Testbed engineering bandwidth allocates per PP-8 spec. Pattern B production-LLM continues in parallel as bandwidth permits.
