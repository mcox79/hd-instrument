# Prereg: wave14_moe_hebbian_anchor_router_v1

**Filed:** 2026-05-27
**Script:** experiments/exp_wave14_moe_hebbian_anchor_router_v1.py
**Queue:** remote_cpu_queue (CPU)
**Trigger:** wave14_moe_cosine_router_v1 HARD_FAIL (routing_entropy > 3.0b at K=16)

## Hypothesis

Cosine_router_v1 used RANDOM BSC anchor vectors which gave routing_entropy ~= log2(K)
(uniform routing = maximum entropy = K bits for K experts). Random anchors in high-dimensional
BSC space are mutually orthogonal, so all queries score nearly equally for all experts.

FIX: Hebbian-learned anchors from the data. anchor_k = sign(sum of top-scoring patterns
for expert k after Phase 1 routing). This creates data-adapted anchors that should
cluster patterns by content, reducing routing entropy.

## Design

Phase 1: Route with random anchors (baseline).
Phase 2: Rebuild anchors via Hebbian bundle of top-scoring patterns per expert.
Re-route with Hebbian anchors. Compare entropy + retention vs random.

3 variants: Hebbian-sign bundle, soft-mean, random (baseline).
K sweep: {4, 8, 16, 32}. N=4096. 3 seeds.

## Pre-registered bands

**HEBBIAN_ROUTER_HARD_PASS:** entropy@K=16 < 2.0b (any variant) AND retention_delta >= -0.015
**HEBBIAN_ROUTER_HARD_FAIL:** entropy > 3.0b for ALL variants
**MIDDLE_BAND:** entropy [2.0, 3.0b] for best variant

## Smoke result

PASS (instrumentation): selftest 5/5 OK; metrics non-null.
Smoke verdict HEBBIAN_ROUTER_HARD_FAIL at N=512 (expected: at smoke N, Hebbian anchors
give near-uniform routing because patterns have very high noise relative to signal).
Ship to N=4096 FULL where the signal-to-noise ratio is higher.

Note: smoke HARD_FAIL is expected per pre-build documentation ("shared-W design means
retention is constant; smoke HARD_FAIL at small N is expected; K_eff~K/2 hypothesis
to be tested at N=4096").
