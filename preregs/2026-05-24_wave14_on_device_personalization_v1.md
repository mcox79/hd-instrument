# Prereg — wave14_on_device_personalization_v1

**Date**: 2026-05-24
**Filed by**: exp_dev role (inline; orchestrator sub-agent compound dispatch for triage-A anchors)
**Routing**: strategy_untested_rows_triage_2026-05-24.md Priority A #3 K3 KILLER T2 (On-device personalization end-to-end); deployment-target match for local_cpu_runner
**Script**: `experiments/exp_wave14_on_device_personalization_v1.py`
**Queue**: local_cpu_queue (CPU-only; deployment-target match)

## Hypothesis

The product spec for K3 KILLER T2 is: a user-laptop loads a base substrate, runs Hebbian updates on user data without GPU/autograd, and retrieves from the resulting bundle at consumer-laptop scale. This is the DEPLOYMENT-TARGET test for the project: local_cpu_runner_local is exactly the platform we expect to ship on.

## Design

Three metrics tested end-to-end at N=2048 on CPU-ONLY:
1. **Add throughput**: how many user items/second can we Hebbian-add to W
2. **Retrieval latency**: ms per single-query read
3. **Base-substrate retention**: how much does W_base degrade after personalization

User data is synthesized as n_user=200 random (byte_idx, pos_idx) bindings. Personalization adds these via Hebbian outer-product. Retention measured by BPC ratio on Phase A test set before/after.

Parameters: N=2048, n_user=200, n_retrievals=100, SEEDS=[7,17,23].

## Falsifier bands (per [[feedback-envelope-expansion-fail-bands]] and [[feedback-no-smoke]])

- **HARD-PASS**: add_throughput >= 100 items/s AND retrieval_latency_ms <= 50 AND retention_A >= 0.70 across 3 seeds. On-device deployment viable at consumer-laptop scale. Substrate-product implication: K3 KILLER T2 closed-PASS; new ✅ row "on-device personalization" opens.
- **HARD-FAIL**: add_throughput <= 10 items/s OR retrieval_latency_ms >= 500 OR retention_A <= 0.30. Substrate not viable for on-device deployment at this scale. Substrate-product implication: K3 closed-FAIL.
- **MIDDLE**: intermediate. Pipeline runs but doesn't meet all product-grade targets.

## Comparison anchors

- existing cpu_platform_timing experiments tested K=4 retrieval at sub-100ms (cap_map row 🟡 inconclusive due to redo timeout)
- this is the first end-to-end test of Hebbian add + retrieval + retention on CPU at deployment scale

## Self-test

`python experiments/exp_wave14_on_device_personalization_v1.py --self-test` verifies 7 verdict-tag cases.

## Pre-reg routing impact

- HARD-PASS → cap_map v188 NEW ✅ "on-device personalization" row; resolves the 🟡 cpu_platform_timing redo
- HARD-FAIL → cap_map v188 K3 closed-FAIL annotation; deployment-target scale not viable
- MIDDLE → annotation; partial deployment-grade viability
